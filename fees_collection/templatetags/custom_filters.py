from django import template

register = template.Library()

@register.filter(name='get_item')
def get_item(dictionary, key):
    """Returns the value from the dictionary for the given key, or 0 if the key does not exist."""
    return dictionary.get(key, 0)

@register.filter(name='indian_number_format')
def indian_number_format(value):
    """
    Converts a number into Indian format: 12,34,567
    """
    try:
        value = int(float(value))  # Convert to float first to handle decimal strings, then to int
    except ValueError:
        return value

    orig = str(value)
    if len(orig) <= 3:
        return orig

    # Separate the last 3 digits
    last_three = orig[-3:]
    # Get the rest of the digits
    other_digits = orig[:-3]

    # Split other_digits into groups of 2
    groups = []
    while other_digits:
        groups.append(other_digits[-2:])
        other_digits = other_digits[:-2]

    # Combine groups and last three digits
    formatted = ','.join(reversed(groups)) + ',' + last_three
    return formatted

@register.filter(name='to_float')
def to_float(value):
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0

@register.filter(name='add')
def add(value, amount):
    return value + amount

@register.filter(name='dict_lookup')
def dict_lookup(dictionary, key):
    """Returns the value from the dictionary for the given key, or 0 if the key does not exist."""
    return dictionary.get(key, 0)
