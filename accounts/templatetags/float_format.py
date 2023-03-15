from django import template
register = template.Library()


@register.filter(name='float_format')
def float_format(value):
    
    fvalue = "{:,.2f}".format(value/100)
    return fvalue