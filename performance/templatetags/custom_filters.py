import re
from django import template

register = template.Library()

@register.filter
def regex_replace(value, args):
    pattern, replacement = args.split(',')
    return re.sub(pattern, replacement, value)

@register.filter
def regex_search(value, pattern):
    match = re.search(pattern, value)
    return match.group(0) if match else ''

@register.filter
def trim(value):
    return value.strip()
