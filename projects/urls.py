from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include

from django.contrib.auth.decorators import login_required
from .views import ProjectListView, ProjectDetailListView, CartView, IncreaseQuantityView, DecreaseQuantityView, RemoveFromCartView
from . import views

urlpatterns = [
    path('', ProjectListView.as_view(), name='projects'),
    path('cart', CartView.as_view(), name='summary'),
    path('crear', login_required(views.crear), name='crear'),
    path('editar/<str:pk>', login_required(views.editar), name='editar'),
    path('eliminar/<str:pk>', login_required(views.eliminar), name='eliminar'),
    path('<slug>/', ProjectDetailListView.as_view(), name='project-detail'),
    path('increase-quantity/<pk>/', 
         IncreaseQuantityView.as_view(), name='increase-quantity'),
    path('decrease-quantity/<pk>/', 
         DecreaseQuantityView.as_view(), name='decrease-quantity'),
    path('remove-from-cart/<pk>/', 
         RemoveFromCartView.as_view(), name='remove-from-cart'),
]
