from django.contrib import admin
from django.urls import path, re_path
from django.conf.urls import url, include

from .views import payment_method_view, payment_method_createview

urlpatterns = [ 
    path('billing/payment-method', payment_method_view, name='payment-method'),
    re_path('billing/payment-method/create/$', payment_method_createview, name='billing-payment-method-endpoint',)
]