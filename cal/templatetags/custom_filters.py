from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Get item from dictionary by key"""
    return dictionary.get(key, {})

@register.filter
def cut(value, arg):
    """Remove all occurrences of arg from the given string"""
    return value.replace(arg, '')