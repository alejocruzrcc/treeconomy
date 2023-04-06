from django import forms
from .models import CommentCompany

class CommentCompanyForm(forms.ModelForm):
    class Meta:
        model = CommentCompany
        fields = ('name', 'email', 'body')
