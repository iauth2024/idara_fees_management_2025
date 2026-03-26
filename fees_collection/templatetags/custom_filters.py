# your_app/templatetags/custom_filters.py
from django import template
from django.template.defaultfilters import stringfilter
import decimal

register = template.Library()

@register.filter
def indian_number_format(value):
    """Convert number to Indian number format (e.g., 12,34,567)"""
    try:
        if value is None:
            return "0.00"
        
        # Convert to float
        value = float(value)
        
        # Format with commas
        s = f"{value:,.2f}"
        
        # Replace western commas with Indian format
        # Western: 1,234,567.00 -> Indian: 12,34,567.00
        parts = s.split('.')
        integer_part = parts[0]
        
        # Convert to Indian format
        if len(integer_part) > 3:
            # Get last 3 digits
            last_three = integer_part[-3:]
            # Get remaining part
            rest = integer_part[:-3]
            # Add commas after every 2 digits
            if rest:
                # Remove existing commas
                rest = rest.replace(',', '')
                # Group in pairs from right
                groups = []
                for i in range(len(rest), 0, -2):
                    start = max(0, i-2)
                    groups.append(rest[start:i])
                # Reverse and join with commas
                rest = ','.join(reversed(groups))
                integer_part = rest + ',' + last_three
            else:
                integer_part = last_three
        else:
            integer_part = integer_part
        
        return f"{integer_part}.{parts[1]}"
    except (ValueError, TypeError, decimal.InvalidOperation):
        return "0.00"

@register.filter
def divide(value, arg):
    """Divide value by arg"""
    try:
        value = float(value) if value is not None else 0
        arg = float(arg) if arg is not None else 1
        if arg != 0:
            return value / arg
        return 0
    except (ValueError, TypeError, ZeroDivisionError):
        return 0

@register.filter
def multiply(value, arg):
    """Multiply value by arg"""
    try:
        value = float(value) if value is not None else 0
        arg = float(arg) if arg is not None else 0
        return value * arg
    except (ValueError, TypeError):
        return 0

@register.filter
def subtract(value, arg):
    """Subtract arg from value"""
    try:
        value = float(value) if value is not None else 0
        arg = float(arg) if arg is not None else 0
        return value - arg
    except (ValueError, TypeError):
        return 0

@register.filter
def add(value, arg):
    """Add arg to value"""
    try:
        value = float(value) if value is not None else 0
        arg = float(arg) if arg is not None else 0
        return value + arg
    except (ValueError, TypeError):
        return 0

@register.filter
def get_percentage(paid, total):
    """Calculate percentage"""
    try:
        paid = float(paid) if paid is not None else 0
        total = float(total) if total is not None else 0
        if total > 0:
            return (paid / total) * 100
        return 0
    except (ValueError, TypeError, ZeroDivisionError):
        return 0