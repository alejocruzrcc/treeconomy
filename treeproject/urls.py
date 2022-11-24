"""bookmarks URL Configuration
The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.views import static
from django.conf.urls.static import static
import accounts

from projects.views import ProjectListView
from django.contrib.auth.decorators import login_required
from accounts import views as account_views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('account/',include('accounts.urls')),
    path('projects/',include('projects.urls')),
    path('billing/',include('billing.urls')),
    path('social-auth/',include('social_django.urls',namespace='social')),
    path('',ProjectListView.as_view(), name='projects'),
    path('contact/', accounts.views.ContactView.as_view(), name="contact"),
    #path('dashboard/',account.views.dashboard,name='dashboard'),
    path('dashboard/', include('dashboard.urls')),
    path('exportclientsxls/', login_required(account_views.export_clients_xls), name='exportclientsxls'),
    path('exportordersxls/', login_required(account_views.export_orders_xls), name='exportordersxls'),
    
] 
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)