from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include

from django.contrib.auth.decorators import login_required
from .views import ProjectListView, ProjectDetailListView

urlpatterns = [
    path('', login_required(ProjectListView.as_view()), name='projects'),
    path('<str:pk>', login_required(ProjectDetailListView.as_view()), name='project-detail')
]