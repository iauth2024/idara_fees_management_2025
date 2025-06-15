import requests
import logging

logger = logging.getLogger(__name__)

def send_telegram_alert(symbol, screener_name, stock_details):
    """
    Send a Telegram alert with stock details.
    """
    BOT_TOKEN = "7816868160:AAFNuK-wKj---yISOPPAHilJXo7B4xYS9v0"  # Replace with your Telegram Bot Token
    CHAT_ID = "5212928367"     # Replace with your Telegram Chat ID

    message = f"New Stock Alert!\n\n{screener_name}\n{stock_details}"
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        # Optional: Remove or change parse_mode if needed
        # "parse_mode": "Markdown"
    }

    try:
        response = requests.post(url, data=payload, timeout=30)  # Increased timeout for reliability
        if response.status_code == 200:
            logger.info(f"Telegram alert sent for {symbol} in {screener_name}")
            return True
        else:
            logger.error(f"Telegram API error for {symbol}: Status {response.status_code}, Response: {response.text}")
            return False
    except Exception as e:
        logger.error(f"Telegram API connection error for {symbol}: {e}")
        return False