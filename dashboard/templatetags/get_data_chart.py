from django import template
register = template.Library()


@register.filter(name='get_data_chart')
def get_data_chart(dict, pro):
    
    data = dict[pro]

    return data