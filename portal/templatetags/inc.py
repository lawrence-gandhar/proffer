from django import template

register = template.Library()

@register.filter
def inc(value, arg):
	arg = int(arg)
	value = value + arg
	return int(value)