from django.contrib import admin
from django.urls import path, re_path
from django.conf.urls import url, include
from django.contrib.auth.decorators import login_required
from .views import generatePdf as GeneratePdf
from .views import *
from . import views

app_name = "billing"
urlpatterns = [ 
    path('payment/config/', views.stripe_config),
    path('cartera', login_required(CarteraView.as_view()), name='cartera'),
    path('orders/<pk>', login_required(GeneratePdf), name='order-detail'),
    path('plantilla/<pk>', login_required(PlantillaOrderView.as_view()), name='plantilla-order-view'),
    path('checkout', CheckoutView.as_view(), name='checkout'),
    re_path(r'^pdf/(?P<cid>[0-9]+)/(?P<value>[a-zA-Z0-9 :._-]+)/$', GeneratePdf, name='pdf'),
    path('create-subscription/', CreateSubscriptionView.as_view(), name='create-subscription'),
    path('success/', PaymentSuccessView.as_view(), name='success'),
    path('retry-invoice/', RetryInvoiceView.as_view(), name='retry-invoice'),
    path('cancelled/', PaymentCancelledView.as_view(), name='cancelled'),
    path('failed/', PaymentFailedView.as_view(), name='failed'),
    path('history/', OrderHistoryListView.as_view(), name='history'),
    path('webhook/', views.webhook, name='webhook'),
   
]
  