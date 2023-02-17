from django import template
import stripe
from datetime import datetime
import locale
locale.setlocale(locale.LC_TIME, '')

register = template.Library()


@register.filter(name='subsItem_created_at')
def subsItem_created_at(item_id):
    print(item_id)
    if item_id != None:
        item = stripe.SubscriptionItem.retrieve(
            item_id,
        )
        fecha = datetime.utcfromtimestamp(item['created']).strftime('%d %b %Y')
    else: 
        fecha= "No Dosponible"
    return fecha

@register.filter(name='subsItem_nextpayment')
def subsItem_nextpayment(user):
    subs_id = user.subscription.stripe_subscription_id
    subs= stripe.Subscription.retrieve(
        subs_id,
    )
    fecha = datetime.utcfromtimestamp(subs['current_period_end']).strftime('%d %B %Y')
    return fecha