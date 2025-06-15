import time
import logging
from django.core.management.base import BaseCommand
from Lucky_Bulls.models import TradingAccount, MonitorControl
from dhanhq import dhanhq
from django.db import transaction
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("monitor_orders.log"),  # Log to a file for production
        logging.StreamHandler(),  # Also output to console
    ],
)

class Command(BaseCommand):
    help = "Monitor orders and copy them with a multiplier from master to child accounts"

    def add_arguments(self, parser):
        parser.add_argument("--poll-interval", type=int, default=5, help="Polling interval in seconds when ON")
        parser.add_argument("--off-interval", type=int, default=36000, help="Sleep interval in seconds when OFF (10 hours)")

    def is_market_open(self):
        now = datetime.now()
        is_weekday = now.weekday() < 5
        is_within_hours = (now.hour == 9 and now.minute >= 0) or (9 < now.hour < 15) or (now.hour == 15 and now.minute <= 35)
        return is_weekday and is_within_hours

    def is_monitor_active(self):
        control, _ = MonitorControl.objects.get_or_create(id=1, defaults={'is_active': True})
        return control.is_active

    def copy_order(self, order_details, multiplier, dhan_client):
        try:
            mapped_order = order_details.copy()
            if "quantity" in mapped_order:
                mapped_order["quantity"] = int(mapped_order["quantity"] * multiplier)

            order_params = {
                "security_id": mapped_order.get("securityId"),
                "exchange_segment": mapped_order.get("exchangeSegment"),
                "transaction_type": mapped_order.get("transactionType"),
                "quantity": mapped_order.get("quantity", 0),
                "price": mapped_order.get("price", 0),
                "trigger_price": mapped_order.get("triggerPrice", 0),
                "product_type": mapped_order.get("productType"),
                "order_type": mapped_order.get("orderType"),
                "validity": mapped_order.get("validity", "DAY"),
                "disclosed_quantity": mapped_order.get("disclosedQuantity", 0),
            }

            if not self.is_market_open() or mapped_order.get("afterMarketOrder", False):
                order_params["after_market_order"] = True
                order_params["amo_time"] = "OPEN"

            order_params = {k: v for k, v in order_params.items() if v is not None}
            response = dhan_client.place_order(**order_params)
            logging.info(f"✅ Order placed successfully: {response}")
            return response
        except Exception as e:
            logging.error(f"🚨 Error placing order: {e}")
            return None

    def handle(self, *args, **options):
        poll_interval = options["poll_interval"]
        off_interval = options["off_interval"]  # 10 hours default
        self.order_mapping = {}
        self.master_order_history = {}
        processed_orders = set()

        logging.info(f"🚀 Starting order monitoring with poll interval: {poll_interval}s, off interval: {off_interval}s")

        while True:
            if not self.is_monitor_active():
                logging.info(f"⏸️ Monitoring is OFF. Sleeping for {off_interval} seconds to avoid API limits.")
                time.sleep(off_interval)
                continue

            if not self.is_market_open():
                logging.info(f"🌙 Market is closed. Sleeping for {poll_interval} seconds.")
                time.sleep(poll_interval)
                continue

            try:
                with transaction.atomic():
                    main_account = TradingAccount.objects.select_for_update().filter(is_master=True).first()
                    if not main_account:
                        logging.warning("⚠️ No master account found.")
                        break

                    main_dhan = dhanhq(main_account.client_id, main_account.token)
                    child_accounts = TradingAccount.objects.filter(is_child=True, parent_account=main_account)

                    master_holdings_response = main_dhan.get_holdings()
                    master_holdings = (
                        {h["securityId"]: h.get("totalQty", 0) for h in master_holdings_response["data"]}
                        if master_holdings_response.get("status") == "success" else {}
                    )

                    orders_response = main_dhan.get_order_list()
                    if orders_response.get("status") != "success" or "data" not in orders_response:
                        logging.warning(f"⚠️ No valid orders found: {orders_response}")
                        time.sleep(poll_interval)
                        continue

                    orders = orders_response["data"]
                    current_master_orders = {order["orderId"]: order for order in orders}

                    for order in orders:
                        order_id = order.get("orderId")
                        security_id = order.get("securityId")
                        transaction_type = order.get("transactionType")
                        quantity = order.get("quantity", 0)

                        if order_id not in processed_orders and order.get("orderStatus") == "PENDING":
                            logging.info(f"🔄 Processing new pending order: {order}")
                            child_order_ids = {}
                            for child_account in child_accounts:
                                child_dhan = dhanhq(child_account.client_id, child_account.token)
                                child_holdings_response = child_dhan.get_holdings()
                                child_positions_response = child_dhan.get_positions()

                                child_holdings = (
                                    {h["securityId"]: h.get("availableQty", 0) for h in child_holdings_response["data"]}
                                    if child_holdings_response.get("status") == "success" else {}
                                )
                                child_positions = (
                                    {p["securityId"]: p.get("netQty", 0) for p in child_positions_response["data"]}
                                    if child_positions_response.get("status") == "success" else {}
                                )

                                if transaction_type == "SELL":
                                    master_quantity = master_holdings.get(security_id, 0)
                                    child_quantity = child_holdings.get(security_id, 0)
                                    child_position_qty = child_positions.get(security_id, 0)

                                    if security_id not in child_holdings and security_id not in child_positions:
                                        logging.info(f"Skipping sell order for child {child_account.client_id} - Symbol not found")
                                        continue

                                    if master_quantity > 0 and (child_quantity > 0 or child_position_qty > 0):
                                        base_quantity = child_quantity if child_quantity > 0 else child_position_qty
                                        proportional_sell_qty = int((base_quantity / master_quantity) * quantity)
                                        if proportional_sell_qty > 0:
                                            order["quantity"] = proportional_sell_qty
                                            response = self.copy_order(order, 1, child_dhan)
                                            if response and response.get("status") == "success":
                                                child_order_ids[child_account.client_id] = response["data"]["orderId"]

                            self.order_mapping[order_id] = {"child_orders": child_order_ids, "original_details": order.copy()}
                            self.master_order_history[order_id] = order.copy()
                            processed_orders.add(order_id)

            except Exception as e:
                logging.error(f"❌ An error occurred: {e}")
            time.sleep(poll_interval)