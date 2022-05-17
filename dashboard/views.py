import pandas as pd
import numpy as np
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.shortcuts import render
from projects.models import Project
from account.models import ProjectByInvestor
from django.core import serializers
from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect


PALETTE = ['#465b65', '#184c9c', '#d33035', '#ffc107', '#28a745', '#6f7f8c', '#6610f2', '#6e9fa5', '#fd7e14', '#e83e8c', '#17a2b8', '#6f42c1' ]

def argon(request):
    projects = Project.objects.all()
    return render(request, 'argon.html',{
        'projects': projects,
    })
