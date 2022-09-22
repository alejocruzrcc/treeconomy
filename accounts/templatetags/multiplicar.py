from django import template
register = template.Library()


@register.filter(name='multiplicar')
def multiplicar(producto, cantidad):
    total = "{:.2f}".format((producto/100)* cantidad) 

    return total