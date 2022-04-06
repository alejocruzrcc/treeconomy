from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include

from django.contrib.auth.decorators import login_required
from .views import ProjectListView, ProjectDetailListView
from . import views

urlpatterns = [
    path('', ProjectListView.as_view(), name='projects'),
    path('crear', login_required(views.crear), name='crear'),
    path('editar/<str:pk>', login_required(views.editar), name='editar'),
    path('eliminar/<str:pk>', login_required(views.eliminar), name='eliminar'),
    path('<str:pk>', ProjectDetailListView.as_view(), name='project-detail')
]
