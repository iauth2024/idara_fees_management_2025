# In Lucky_Bulls/management/commands/send_alerts.py
from django.core.management.base import BaseCommand
from Lucky_Bulls.models import Performance
from Lucky_Bulls.telegram_utils import send_telegram_alert
from django.utils.timezone import now
import logging
from django.db import transaction

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Sends performance alerts for unsent notifications'

    def handle(self, *args, **options):
        # Fetch performances that haven't been alerted yet
        performances = Performance.objects.filter(alert_sent=False).order_by('-triggered_at')

        if not performances.exists():
            logger.info("No performance alerts to send.")
            return

        logger.info(f"Found {performances.count()} performance(s) to process.")

        # Process performances in batches
        batch_size = 50
        success_count = 0
        failure_count = 0

        for i in range(0, performances.count(), batch_size):
            batch = performances[i:i + batch_size]
            for performance in batch:
                stock_details = (
                    f"Symbol: {performance.symbol}\n"
                    f"Close Price: ₹{performance.initial_price}\n"
                    f"Triggered At: {performance.triggered_at}\n"
                    f"Screener: {performance.screener.name}"
                )
                try:
                    # Send Telegram alert
                    if send_telegram_alert(performance.symbol, performance.screener.name, stock_details):
                        performance.alert_sent = True
                        performance.alert_sent_at = now()
                        success_count += 1
                    else:
                        logger.error(f"Failed to send alert for {performance.symbol}: Telegram API returned False")
                        failure_count += 1
                except Exception as e:
                    logger.error(f"Failed to send alert for {performance.symbol}: {e}")
                    failure_count += 1

            # Bulk update the processed performances
            with transaction.atomic():
                Performance.objects.bulk_update(batch, ['alert_sent', 'alert_sent_at'])

        logger.info(f"Processing complete. Success: {success_count}, Failures: {failure_count}")