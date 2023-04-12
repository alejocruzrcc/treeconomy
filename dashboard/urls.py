from django.urls import path
from . import views
from .views import CompanyListView
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('', login_required(views.dashboard), name='dashboard'),
    path('invest_api',  login_required(views.invest_api), name='invest_api'),
    path('invest',  login_required(views.invest), name='invest'),
    path('companies/',  login_required(CompanyListView.as_view()), name='companies'),
    path('companies/<slug>/', views.dashboard_company, name='dashboard_company'),
]