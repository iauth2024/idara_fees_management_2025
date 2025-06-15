from celery import shared_task
from .models import Order, ChildAccount, Performance
from .telegram_alert import send_telegram_alert
from django.utils.timezone import now
import logging

# Set up logger
logger = logging.getLogger(__name__)

@shared_task
def monitor_master_orders():
    """
    Celery task to monitor master orders and replicate them to child accounts.
    """
    try:
        # Fetch all pending orders from the master account
        master_orders = Order.objects.filter(account__is_master=True, status='PENDING')

        for master_order in master_orders:
            # Fetch child accounts associated with the master account
            child_accounts = ChildAccount.objects.filter(master_account=master_order.account)

            for child_account in child_accounts:
                # Calculate the quantity for the child account
                child_quantity = int(master_order.quantity * child_account.multiplier)

                # Create a new order for the child account
                Order.objects.create(
                    account=child_account,
                    symbol=master_order.symbol,
                    quantity=child_quantity,
                    order_type=master_order.order_type,
                    status='PENDING'
                )

                # Optionally, call your trading API to place the order
                # trading_api.place_order(child_account, master_order.symbol, child_quantity, master_order.order_type)

                logger.info(f"Order replicated for child account {child_account.id}: {master_order.symbol} ({child_quantity} units)")

            # Update the master order status to 'REPLICATED' or 'EXECUTED'
            master_order.status = 'REPLICATED'
            master_order.save()
            logger.info(f"Master order {master_order.id} replicated to child accounts.")

    except Exception as e:
        logger.error(f"Error in monitor_master_orders task: {e}", exc_info=True)

@shared_task
def send_performance_alerts():
    try:
        logger.info("Starting send_performance_alerts task...")
        performances = Performance.objects.filter(alert_sent=False).order_by('-triggered_at')
        logger.info(f"Found {len(performances)} unsent alerts.")

        for performance in performances:
            stock_details = (
                f"Symbol: {performance.symbol}\n"
                f"Close Price: ₹{performance.initial_price}\n"
                f"Triggered At: {performance.triggered_at}\n"
                f"Screener: {performance.screener.name}"
            )
            logger.info(f"Preparing alert for {performance.symbol}...")

            try:
                send_telegram_alert(performance.symbol, performance.screener.name, stock_details)
                performance.alert_sent = True
                performance.alert_sent_at = now()
                performance.save()
                logger.info(f"Alert sent for {performance.symbol}.")
            except Exception as e:
                logger.error(f"Failed to send alert for {performance.symbol}: {e}", exc_info=True)

    except Exception as e:
        logger.error(f"Error in send_performance_alerts task: {e}", exc_info=True)