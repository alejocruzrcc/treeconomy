from django.forms import ModelForm 
from django.urls import reverse
from django import forms
from .models import Project

from account.models import ProjectByInvestor, User

class ProjectForm(forms.ModelForm):  
    class Meta:
        model = Project
        fields = "__all__"
        


class BuyProjectForm(ModelForm):
    pass