from django import template

register = template.Library()

@register.filter
def dict_get(dictionary, key):
    """Safely get a value from a dictionary using a key."""
    if dictionary and isinstance(dictionary, dict):
        return dictionary.get(key, None)
    return None
from django import template

register = template.Library()

@register.filter
def get_item(value, key):
    """
    Custom filter to fetch a value from a dictionary by key.
    If the input is not a dictionary, return 'N/A'.
    """
    if isinstance(value, dict):  # Check if the input is a dictionary
        return value.get(key, "N/A")
    return "N/A"  # Return 'N/A' if the input is not a dictionary