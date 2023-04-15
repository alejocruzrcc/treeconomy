from django import forms
from .models import CommentCompany

class CommentCompanyForm(forms.ModelForm):
    class Meta:
        model = CommentCompany
        fields = ('name', 'email', 'body')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for field in ['name', 'email', 'body']:
            self.fields[field].widget.attrs['class'] = 'form-control form-control-lg'
