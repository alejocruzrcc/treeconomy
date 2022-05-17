from django.urls import path
from . import views

urlpatterns = [
    path('', views.argon, name='argon_data'),
]