from django import template
from django.template.defaultfilters import stringfilter
import re

register = template.Library()

@register.filter(name='article_meta')
@stringfilter
def article_meta(value):
	if is_url(value):
		return "<a href='%s' targer='_blank'>%s</a>" % (value, value)
	else:
		return value

def is_url(url):
	regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

	return regex.match(url)

register.filter('article_meta', article_meta)
