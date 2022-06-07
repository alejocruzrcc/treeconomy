from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.utils.http import is_safe_url

import stripe

STRIPE_SECRET_KEY = getattr(settings, "STRIPE_SECRET_KEY", 'sk_test_EHJpOxVYLVcHnv6WpVadsWct00lDPscWIx')
STRIPE_PUB_KEY = getattr(settings, "STRIPE_PUB_KEY", 'pk_test_4hzA0ERMQ6QMkQktzYyxV1L200XyAHRFLx')
stripe.api_key = STRIPE_SECRET_KEY

from .models import BillingProfile, Card

def cartera_view(request):
    return render(request,'billing/cartera.html',{'section':'cartera'})

def payment_method_view(request):
    #next_url = 
    # if request.user.is_authenticated():
    #     billing_profile = request.user.billingprofile
    #     my_customer_id = billing_profile.customer_id

    billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request)
    if not billing_profile:
        return redirect("/cart")
    next_url = None
    next_ = request.GET.get('next')
    #next_ = request.GET['next']
    print(next_)
    if is_safe_url(next_, request.get_host()):
        next_url = next_
    return render(request, 'billing/payment-method.html', {"publish_key": STRIPE_PUB_KEY, "next_url": next_url})


def payment_method_createview(request):
    if request.method == "POST" and request.is_ajax():
        print('im in create')
        billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request)
        if not billing_profile:
            return HttpResponse({"message": "Cannot find this user"}, status=401)
        token = request.POST.get("token")
        if token is not None:
            print('token is not none')
            Card.objects.add_new(billing_profile, token)
        return JsonResponse({"message": "Success! Your card was added."})
    
    return HttpResponse("error", status=401)