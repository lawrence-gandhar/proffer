from django import template

register = template.Library()

@register.filter
def sub(value, arg):
	arg = int(arg)
	return int(value - arg)