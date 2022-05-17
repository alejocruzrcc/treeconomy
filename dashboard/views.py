import pandas as pd
import numpy as np
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.shortcuts import render
from projects.models import Project
from account.models import ProjectByInvestor
from django.core import serializers
from django.template import loader


def dashboard(request):
    projects = Project.objects.all()
    return render(request, 'argon.html',{
        'projects': projects,
    })
