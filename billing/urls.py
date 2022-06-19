from django.contrib import admin
from django.urls import path, re_path
from django.conf.urls import url, include
from .views import *
from . import views

app_name = "billing"
urlpatterns = [ 
    path('payment/config/', views.stripe_config),
    path('cartera', cartera_view, name='cartera'),
    path('checkout', CheckoutView.as_view(), name='checkout'),
    path('create-subscription/', CreateSubscriptionView.as_view(), name='create-subscription'),
    path('success/', PaymentSuccessView.as_view(), name='success'),
    path('retry-invoice/', RetryInvoiceView.as_view(), name='retry-invoice'),
    path('cancelled/', PaymentCancelledView.as_view(), name='cancelled'),
    path('failed/', PaymentFailedView.as_view(), name='failed'),
    path('history/', OrderHistoryListView.as_view(), name='history'),
   
]
  