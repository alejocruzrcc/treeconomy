from django import template
register = template.Library()


@register.filter(name='activos')
def activos(lista):
    total = lista.filter(active=True)
    return total

@register.filter(name='inactivos')
def activos(lista):
    total = lista.filter(active=False)
    return total