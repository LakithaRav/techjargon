from django import template
import re

register = template.Library()

@register.filter(name='range')
def filter_range(start, end):
  return range(start, end)

register.filter('range', filter_range)
