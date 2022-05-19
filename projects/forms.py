from django.forms import ModelForm 
from django.urls import reverse
from django import forms
from .models import OrderItem, Project

from account.models import ProjectByInvestor, User

class ProjectForm(forms.ModelForm):  
    class Meta:
        model = Project
        fields = "__all__"
        exclude = ('slug',)
        
class ProjectByInvestorForm(forms.ModelForm):  
    total_price = forms.FloatField(
        widget=forms.TextInput(attrs={'readonly':'readonly'})
    )
    unit_price = forms.FloatField(
        widget=forms.TextInput(attrs={'readonly':'readonly'})
    )
    class Meta:
        model = ProjectByInvestor
        fields = "__all__"

class AddToCartForm(forms.ModelForm):
    class Meta: 
        model = OrderItem
        fields = ['quantity', 'type_inversion']
    
    def __init__(self, *args, **kwargs):
        project_id = kwargs.pop('project_id')
        project = Project.objects.get(name=project_id)
        super().__init__(*args, **kwargs)
        
        
        
        