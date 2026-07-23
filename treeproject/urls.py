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
from django.urls import path, include, re_path
from django.conf import settings
from django.views.static import serve as static_serve
from django.conf.urls.static import static as static_urls
import accounts
from .views import *
from billing.views import *
from projects.views import ProjectListView
from django.contrib.auth.decorators import login_required
from accounts import views as account_views
from django.conf.urls.i18n import i18n_patterns

urlpatterns = [
    path('admin/', admin.site.urls),
    path('account/', include('accounts.urls')),
    path('projects/', include('projects.urls')),
    path('billing/', include('billing.urls')),
    path('social-auth/', include('social_django.urls', namespace='social')),
    path('', ProjectListView.as_view(), name='projects'),
    path('contact/', accounts.views.ContactView.as_view(), name="contact"),
    # path('dashboard/',account.views.dashboard,name='dashboard'),
    path('dashboard/', include('dashboard.urls')),
    path('exportclientsxls/', login_required(account_views.export_clients_xls), name='exportclientsxls'),
    path('exportordersxls/', login_required(account_views.export_orders_xls), name='exportordersxls'),
    path('exportclientspag/', login_required(account_views.export_clients_pag), name='exportclientspag'),
    path('exportorderspag/', login_required(account_views.export_orders_pag), name='exportorderspag'),
]

urlpatterns = [
    *i18n_patterns(*urlpatterns, prefix_default_language=True),
    path("set_language/<str:language>", set_language, name="set-language"),
]

urlpatterns += [
    path('billing/webhook/', webhook, name='webhook'),
]

# Serve collected static files in production (DEBUG=False). Without this,
# missing WhiteNoise files return Django HTML 404 and browsers report MIME errors.
urlpatterns += [
    re_path(
        r'^static/(?P<path>.*)$',
        static_serve,
        {'document_root': settings.STATIC_ROOT},
    ),
]

if settings.DEBUG:
    urlpatterns += static_urls(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
