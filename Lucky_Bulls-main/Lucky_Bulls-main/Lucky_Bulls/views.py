from django.shortcuts import render
# Create your views here.
from django.http import JsonResponse
from dhanhq import dhanhq
from .models import TradingAccount
# prompt: AttributeError at /trading_data/
# 'dhanhq' object has no attribute 'get_holdings_data'

from django.shortcuts import render

from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import TradingAccount
from .forms import TradingAccountForm
from django.http import JsonResponse
from django.shortcuts import render
from dhanhq import dhanhq
from .models import TradingAccount
import logging
import requests


# DhanHQ API Wrapper Class
class dhanhq:
    def __init__(self, client_id, access_token, disable_ssl=False, pool=None):
        """
        Initialize the dhanhq class with client ID and access token.

        Args:
            client_id (str): The client ID for the trading account.
            access_token (str): The access token for API authentication.
            disable_ssl (bool): Flag to disable SSL verification.
            pool (dict): Optional connection pool settings.
        """
        self.client_id = str(client_id)
        self.access_token = access_token
        self.base_url = 'https://api.dhan.co/v2'
        self.timeout = 10  # Timeout for API requests
        self.session = requests.Session()
        self.header = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
        }
        if disable_ssl:
            self.session.verify = False

    def _parse_response(self, response):
        """
        Parse the API response and handle errors.

        Args:
            response (requests.Response): The response object.

        Returns:
            dict: Parsed response or error message.
        """
        if response.status_code == 200:
            try:
                return response.json()
            except ValueError as e:
                logging.error('Error parsing JSON response: %s', e)
                return {
                    'status': 'failure',
                    'remarks': 'Invalid JSON response',
                    'data': '',
                }
        else:
            logging.error('API error: %s', response.text)
            return {
                'status': 'failure',
                'remarks': response.text,
                'data': '',
            }
   

# Django View for Trading Data
from django.http import JsonResponse
from django.shortcuts import render
from dhanhq import dhanhq
from .models import TradingAccount
import logging

logging.basicConfig(level=logging.INFO)  # Set logging level to INFO for better visibility

from django.shortcuts import render
import logging



# Configure logging for the view function
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from django.shortcuts import render
from .models import TradingAccount
from .dhanhq import dhanhq  # Assuming you have a function to interact with Dhan API
import logging

# Initialize the logger
logger = logging.getLogger(__name__)
from dhanhq import dhanhq
import logging
from django.shortcuts import render
from .models import TradingAccount

logger = logging.getLogger(__name__)

def fetch_fund_limits(dhan_client):
    """Fetches fund limits for a Dhan account."""
    try:
        fund_limits = dhan_client.get_fund_limits()
        return fund_limits.get('data', {}).get('availabelBalance', 'N/A')  # Adjust key spelling if necessary
    except Exception as e:
        logger.error(f"Error fetching fund limits: {e}")
        return None

def fetch_holdings(dhan_client):
    """Fetches holdings for a Dhan account."""
    try:
        holdings = dhan_client.get_holdings()
        if holdings and 'data' in holdings:
            return [
                {
                    'Symbol': holding.get('tradingSymbol', 'N/A'),
                    'Total Quantity': holding.get('totalQty', 'N/A'),
                    'Average Cost Price': holding.get('avgCostPrice', 'N/A'),
                }
                for holding in holdings['data']
            ]
        return "No holdings data available."
    except Exception as e:
        logger.error(f"Error fetching holdings: {e}")
        return None

def fetch_positions(dhan_client):
    """Fetches positions for a Dhan account."""
    try:
        positions = dhan_client.get_positions()
        if positions and 'data' in positions:
            return [
                {
                    'tradingSymbol': position.get('tradingSymbol', 'N/A'),
                    'buyQty': position.get('buyQty', 'N/A'),
                    'sellQty': position.get('sellQty', 'N/A'),
                    'netQty': position.get('netQty', 'N/A'),
                    'realizedProfit': position.get('realizedProfit', 'N/A'),
                    'unrealizedProfit': position.get('unrealizedProfit', 'N/A'),
                }
                for position in positions['data']
            ]
        return "No positions data available."
    except Exception as e:
        logger.error(f"Error fetching positions: {e}")
        return None
def fetch_orders(dhan_client):
    """Fetches and filters the orders for a Dhan account."""
    try:
        orders = dhan_client.get_order_list()
        if orders and 'data' in orders:
            filtered_orders = []
            for order in orders['data']:
                filtered_order = {
                    'orderStatus': order.get('orderStatus', 'N/A'),
                    'transactionType': order.get('transactionType', 'N/A'),
                    'exchangeSegment': order.get('exchangeSegment', 'N/A'),
                    'productType': order.get('productType', 'N/A'),
                    'orderType': order.get('orderType', 'N/A'),
                    'validity': order.get('validity', 'N/A'),
                    'tradingSymbol': order.get('tradingSymbol', 'N/A'),
                    'securityId': order.get('securityId', 'N/A'),
                    'quantity': order.get('quantity', 'N/A'),
                    'disclosedQuantity': order.get('disclosedQuantity', 'N/A'),
                    'price': order.get('price', 'N/A'),
                    'triggerPrice': order.get('triggerPrice', 'N/A'),
                    'afterMarketOrder': order.get('afterMarketOrder', 'N/A'),
                    'createTime': order.get('createTime', 'N/A'),
                    'updateTime': order.get('updateTime', 'N/A'),
                }
                filtered_orders.append(filtered_order)
            return filtered_orders
        else:
            return "No orders data available."
    except Exception as e:
        return f"Error fetching orders: {e}"


import time
import logging
from django.shortcuts import render
from .models import TradingAccount

logger = logging.getLogger(__name__)

import logging

logger = logging.getLogger(__name__)


import time
import logging
import threading
from django.shortcuts import render
from .models import TradingAccount
from .dhanhq import dhanhq  # Ensure this is the correct import for your Dhan API wrapper

logger = logging.getLogger(__name__)

def fetch_orders(dhan_client):
    """Fetches and filters the orders for a Dhan account."""
    try:
        orders = dhan_client.get_order_list()  # Ensure this is the correct method name
        if orders and 'data' in orders:
            filtered_orders = []
            for order in orders['data']:
                filtered_order = {
                    'orderStatus': order.get('orderStatus', 'N/A'),
                    'transactionType': order.get('transactionType', 'N/A'),
                    'exchangeSegment': order.get('exchangeSegment', 'N/A'),
                    'productType': order.get('productType', 'N/A'),
                    'orderType': order.get('orderType', 'N/A'),
                    'validity': order.get('validity', 'N/A'),
                    'tradingSymbol': order.get('tradingSymbol', 'N/A'),
                    'securityId': order.get('securityId', 'N/A'),
                    'quantity': order.get('quantity', 'N/A'),
                    'disclosedQuantity': order.get('disclosedQuantity', 'N/A'),
                    'price': order.get('price', 'N/A'),
                    'triggerPrice': order.get('triggerPrice', 'N/A'),
                    'afterMarketOrder': order.get('afterMarketOrder', 'N/A'),
                    'createTime': order.get('createTime', 'N/A'),
                    'updateTime': order.get('updateTime', 'N/A'),
                }
                filtered_orders.append(filtered_order)
            return filtered_orders
        else:
            return "No orders data available."
    except Exception as e:
        logger.error(f"Error fetching orders: {e}")
        return f"Error fetching orders: {e}"



def trading_data_view(request):
    """Fetches trading data and copies master orders to child accounts."""
    
    # Initialize accounts if not already present
    if not TradingAccount.objects.exists():
        try:
            TradingAccount.objects.create(
                name="Master Account", client_id="master123", token="mastertoken", is_master=True
            )
            TradingAccount.objects.create(
                name="Child Account 1", client_id="child123", token="childtoken1", is_child=True, multiplier=1.5
            )
            TradingAccount.objects.create(
                name="Child Account 2", client_id="child456", token="childtoken2", is_child=True, multiplier=2.0
            )
            logger.info("Accounts initialized successfully.")
        except Exception as e:
            logger.error(f"Error initializing accounts: {e}")
            return render(request, 'error.html', {'error_message': "Error initializing accounts."})

    # Fetch accounts from the database
    accounts = TradingAccount.objects.all()
    if not accounts:
        logger.error("No accounts found in the database.")
        return render(request, 'error.html', {'error_message': "No trading accounts found."})

    master_account = None
    child_accounts_data = []
    child_accounts = []  # Store child accounts for order copying

    # Process each account and fetch data
    for account in accounts:
        dhan_client = dhanhq(account.client_id, account.token)  # Initialize the Dhan client
        try:
            account_data = {
                'name': account.name,
                'client_id': account.client_id,
                'holdings': fetch_holdings(dhan_client),
                'positions': fetch_positions(dhan_client),
                'fund_limits': fetch_fund_limits(dhan_client),
                'orders': fetch_orders(dhan_client),  # Fetch orders for each account
            }
            if account.is_master:
                master_account = account_data
                master_client = dhan_client  # Save master client for monitoring orders
                logger.info(f"Master Account Data: {master_account}")
            elif account.is_child:
                child_accounts.append(account)  # Save child accounts for order copying
                child_accounts_data.append(account_data)
                logger.info(f"Child Account Data: {account_data}")
        except Exception as e:
            logger.error(f"Error processing account {account.name}: {e}")
            continue
    
    # Monitor Master Orders and Copy to Child Accounts

    # Prepare context for the template
    context = {
        'master_account': master_account,
        'child_accounts': child_accounts_data,
    }

    return render(request, 'trading_data.html', context)




# Error View for Handling Exceptions
def error_view(request, exception):
    return render(request, 'error.html', {'error_message': str(exception)})

# List all accounts
class TradingAccountListView(ListView):
    model = TradingAccount
    template_name = 'trading_account_list.html'
    context_object_name = 'accounts'

# Add a new account
class TradingAccountCreateView(CreateView):
    model = TradingAccount
    form_class = TradingAccountForm
    template_name = 'trading_account_form.html'
    success_url = reverse_lazy('trading_account_list')

# Edit an account
class TradingAccountUpdateView(UpdateView):
    model = TradingAccount
    form_class = TradingAccountForm
    template_name = 'trading_account_form.html'
    success_url = reverse_lazy('trading_account_list')

# Delete an account
class TradingAccountDeleteView(DeleteView):
    model = TradingAccount
    template_name = 'trading_account_confirm_delete.html'
    success_url = reverse_lazy('trading_account_list')
from django.shortcuts import render, redirect
from .models import MonitorControl

from django.shortcuts import render, redirect
from .models import MonitorControl, Screener

def index_view(request):
    control, created = MonitorControl.objects.get_or_create(id=1, defaults={'is_active': True})
    screeners = Screener.objects.all()

    if request.method == 'POST':
        is_active = request.POST.get('is_active') == 'on'
        control.is_active = is_active
        control.save()
        return redirect('index_view')

    return render(request, 'index.html', {'control': control, 'screeners': screeners})

##############################################################################################################################
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Screener, Performance
from .forms import ScreenerForm
import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
from datetime import datetime
from django.utils.timezone import now

# Initialize logger
import logging
logger = logging.getLogger(__name__)

#########################################################################################################################
# Screener-Related Views
#########################################################################################################################

def screener_list(request):
    """
    Display a list of all screeners.
    """
    screeners = Screener.objects.all()
    return render(request, "screener_list.html", {"screeners": screeners})


def add_screener(request):
    """
    Add a new screener.
    """
    if request.method == 'POST':
        form = ScreenerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Screener added successfully.")
            return redirect('screener_results')
    else:
        form = ScreenerForm()
    return render(request, 'add_screener.html', {'form': form})


def edit_screener(request, screener_id):
    """
    Edit an existing screener.
    """
    screener = get_object_or_404(Screener, id=screener_id)
    if request.method == 'POST':
        form = ScreenerForm(request.POST, instance=screener)
        if form.is_valid():
            form.save()
            messages.success(request, "Screener updated successfully.")
            return redirect('screener_results')
    else:
        form = ScreenerForm(instance=screener)
    return render(request, 'edit_screener.html', {'form': form, 'screener': screener})


def delete_screener(request, screener_id):
    """
    Delete an existing screener.
    """
    screener = get_object_or_404(Screener, id=screener_id)
    if request.method == 'POST':
        screener.delete()
        messages.success(request, "Screener deleted successfully.")
        return redirect('screener_results')
    return render(request, 'confirm_delete_screener.html', {'screener': screener})
def screener_results(request):
    """
    Fetches and displays results for selected screeners.
    """
    # Fetch all active screeners from the database
    screeners = Screener.objects.filter(is_active=True)
    screener_names = [screener.name for screener in screeners]

    # Get the selected screener from the request
    screener_name = request.GET.get("screener", "ALL")
    logger.info(f"Selected Screener: {screener_name}")  # Log the selected screener

    try:
        data = []
        if screener_name == "ALL":
            # Fetch data for all screeners
            for screener in screeners:
                response = fetch_screener_data({"scan_clause": screener.condition}, screener.name)
                if response is not None:
                    data.extend(response)
        else:
            # Fetch data for the selected screener
            screener = Screener.objects.get(name=screener_name)
            response = fetch_screener_data({"scan_clause": screener.condition}, screener.name)
            if response is not None:
                data = response

        return render(
            request,
            "screener_results.html",
            {
                "stocks": data,
                "screener_name": screener_name,
                "screener_names": screener_names,
            },
        )

    except Exception as e:
        logger.error(f"Error in screener_results: {e}")
        return render(
            request,
            "screener_results.html",
            {
                "error": str(e),
                "screener_name": screener_name,
                "screener_names": screener_names,
            },
        )


from django.core.management.base import BaseCommand
from Lucky_Bulls.models import Performance, Screener
from Lucky_Bulls.telegram_utils import send_telegram_alert
from django.utils.timezone import now
import logging
from django.db import transaction
import requests
from bs4 import BeautifulSoup as bs
import pandas as pd

logger = logging.getLogger(__name__)


#########################################################################################################################
# Performance-Related Views
#########################################################################################################################

def performance_page(request):
    """
    Display performance data with pagination.
    """
    # Fetch all performance data ordered by 'triggered_at' (latest first)
    performances = Performance.objects.all().order_by('-triggered_at')

    # Paginate the results (e.g., 10 items per page)
    paginator = Paginator(performances, 10)
    page_number = request.GET.get('page')  # Get the current page number from the request
    page_obj = paginator.get_page(page_number)  # Get the Page object for the current page

    # Render the template with the paginated performance data
    return render(request, 'performance.html', {'performances': page_obj})



#########################################################################################################################
# Combined Results View
#########################################################################################################################

import logging
import logging

def combined_results(request):
    """
    Fetches combined results from all active screeners and renders them in a template,
    sending Telegram alerts for new stocks.
    """
    logger = logging.getLogger(__name__)

    # Fetch all active screeners from the database
    screeners = Screener.objects.filter(is_active=True)

    combined_data = {}
    for screener in screeners:
        logger.info(f"Fetching data for screener: {screener.name}")
        screener_data = fetch_screener_data({"scan_clause": screener.condition}, screener.name)

        if not screener_data:
            logger.warning(f"No data received for screener: {screener.name}")
            continue

        # Check if 'Date' key exists
        valid_screener_data = []
        for entry in screener_data:
            if 'Date' in entry:
                valid_screener_data.append(entry)
            else:
                logger.warning(f"Entry missing 'Date' key: {entry}")

        # Sort by date if possible
        try:
            screener_data_sorted = sorted(
                valid_screener_data,
                key=lambda x: x.get('Date', '1970-01-01'),
                reverse=True
            )
            combined_data[screener.name] = screener_data_sorted
        except Exception as e:
            logger.error(f"Sorting error for screener '{screener.name}': {e}")

        # Send Telegram alerts for new stocks (if not already handled in fetch_screener_data)
        for stock in screener_data_sorted:
            symbol = stock.get('nsecode', 'Unknown')
            close_price = stock.get('close', 0)
            stock_details = (
                f"Symbol: {symbol}\n"
                f"Close Price: ₹{close_price}\n"
                f"Triggered At: {now()}\n"
                f"Screener: {screener.name}"
            )
            try:
                if send_telegram_alert(symbol, screener.name, stock_details):
                    logger.info(f"Telegram alert sent for {symbol} in {screener.name}")
                else:
                    logger.error(f"Failed to send Telegram alert for {symbol} in {screener.name}")
            except Exception as e:
                logger.error(f"Error sending Telegram alert for {symbol} in {screener.name}: {e}")

    return render(request, 'combined_results.html', {'combined_data': combined_data})

from telegram import Bot
import logging

logger = logging.getLogger(__name__)

