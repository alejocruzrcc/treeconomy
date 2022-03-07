from django.forms import ModelForm 
from django.urls import reverse

from .models import Project

from accounts.models import ProjectByInvestor, User

class BuyProjectForm(ModelForm):
    pass