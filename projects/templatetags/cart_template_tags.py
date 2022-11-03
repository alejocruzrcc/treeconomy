from django import template
from billing.utils import get_or_set_order_session, get_or_zero_order_session

register = template.Library()

@register.filter
def cart_item_count(request):
    order = get_or_zero_order_session(request)
    if order:
        count = order.items.count()
    else:
        count = 0
    return count
    