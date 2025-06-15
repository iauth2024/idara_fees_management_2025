from django.db import models
from django.core.exceptions import ValidationError
from django.utils.timezone import now

# Trading Account Model
class TradingAccount(models.Model):
    name = models.CharField(max_length=100)
    client_id = models.CharField(max_length=100)
    token = models.TextField()
    is_master = models.BooleanField(default=False)
    is_child = models.BooleanField(default=False)
    parent_account = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children'
    )
    multiplier = models.FloatField(
        null=True, blank=True, help_text="Multiplier for child accounts"
    )
    allowed_ips = models.JSONField(default=list, blank=True)  # Store allowed IPs
    restrict_login = models.BooleanField(default=True, help_text="Restrict login based on IP")

    def __str__(self):
        return self.name

    def clean(self):
        """Ensure only child accounts can have a multiplier."""
        if self.is_master and self.multiplier is not None:
            raise ValidationError({"multiplier": "Master accounts cannot have a multiplier."})
        if self.is_child and self.multiplier is None:
            raise ValidationError({"multiplier": "Child accounts must have a multiplier."})
        if self.is_master and self.is_child:
            raise ValidationError("An account cannot be both a master and a child.")

    def get_effective_multiplier(self):
        """Returns the multiplier for child accounts or 1 for master accounts."""
        return self.multiplier if self.is_child else 1.0

from django.db import models

class MonitorControl(models.Model):
    is_active = models.BooleanField(default=True)  # True = ON, False = OFF
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Monitor Control"
        verbose_name_plural = "Monitor Controls"

    def __str__(self):
        return f"Monitor Active: {self.is_active}"
class OrderMapping(models.Model):
    master_order_id = models.CharField(max_length=100)
    child_client_id = models.CharField(max_length=100)
    child_order_id = models.CharField(max_length=100)
    multiplier = models.FloatField()
    original_quantity = models.IntegerField()
    remaining_quantity = models.IntegerField()

    def __str__(self):
        return f"{self.master_order_id} -> {self.child_order_id}"

# Screener Model
class Screener(models.Model):
    name = models.CharField(max_length=100, unique=True)  # Name of the screener
    condition = models.TextField()  # The scan clause or condition
    is_active = models.BooleanField(default=True)  # To enable/disable the screener

    def __str__(self):
        return self.name


# Stock Model
class Stock(models.Model):
    nsecode = models.CharField(max_length=20)
    name = models.CharField(max_length=255)
    bsecode = models.CharField(max_length=20, null=True, blank=True)
    per_chg = models.FloatField()
    close = models.FloatField()
    volume = models.BigIntegerField()
    screener = models.ForeignKey(Screener, on_delete=models.CASCADE, null=True, blank=True)  # Reference to the Screener model

    def __str__(self):
        return self.name


# Performance Model
class Performance(models.Model):
    symbol = models.CharField(max_length=20)
    screener = models.ForeignKey(Screener, on_delete=models.CASCADE)  # Reference to the Screener model
    triggered_at = models.DateTimeField(default=now)
    timeframe = models.CharField(max_length=255)
    initial_price = models.FloatField()

    # New fields for tracking alerts
    alert_sent = models.BooleanField(default=False)  # Indicates if an alert has been sent
    alert_sent_at = models.DateTimeField(null=True, blank=True)  # Time the alert was sent

    def __str__(self):
        return f"{self.symbol} - {self.screener.name}"


# Screener History Model
class ScreenerHistory(models.Model):
    screener = models.ForeignKey(Screener, on_delete=models.CASCADE)  # Reference to the Screener model
    date = models.DateField(auto_now_add=True)
    stocks = models.JSONField()  # Store stock list as JSON

    def __str__(self):
        return f"{self.screener.name} - {self.date}"
    

from django.db import models

class ModifiedOrder(models.Model):
    # Assuming fields based on context, adjust as needed
    dhan_client_id = models.CharField(max_length=50)
    order_id = models.CharField(max_length=50)
    master_order_id = models.CharField(max_length=50, null=True, blank=True)
    new_quantity = models.IntegerField()
    new_price = models.FloatField(null=True, blank=True)
    new_trigger_price = models.FloatField(null=True, blank=True)
    modified_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Modified Order {self.order_id} for {self.dhan_client_id}"