from django import template

register = template.Library()

@register.filter
def poundsafe(value):
    return value.replace('#','\#')
