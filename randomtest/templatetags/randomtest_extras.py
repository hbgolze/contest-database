from django import template

register = template.Library()

@register.filter
def poundsafe(value):
    return value.replace('#','\#')

@register.filter
def surroundbracket(value):
    return '{'+value+'}'

@register.filter
def replacearrow(value):
    return value.replace('>','$\\to$')

@register.filter
def add_class(modelform_input, css_class):
    return modelform_input.as_widget(attrs={'class': css_class})
