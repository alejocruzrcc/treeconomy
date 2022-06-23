from django.forms import ModelForm 
from django.urls import reverse
from django import forms
from .models import OrderItem, Project, Bill, Subscription
from accounts.models import ProjectByInvestor, User

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
        
class SubscriptionForm(forms.ModelForm):
    OPTIONS = (('Active', 'active'), ('Closed', 'closed'), ('On hold', 'On hold'))
    status = forms.ChoiceField(choices=OPTIONS, required=True) 

    class Meta:
        model = Subscription
        fields = ('user', 'n_projects')
    
    def clean_status(self):
        status = self.cleaned_data['status']
        if not status:
            raise forms.ValidationError('You have to provide a status for this subscription')
        
        return status

class BillForm(forms.Form):
    
    billing_address_line_1 = forms.CharField()
    billing_address_line_2 = forms.CharField()
    billing_zip_code = forms.CharField()
    billing_city = forms.CharField()
    
    selected_billing_address = forms.ModelChoiceField(
        Bill.objects.none(), required=False
    )
    
      
    def __init__(self, *args, **kwargs):
        user_id = kwargs.pop('user_id')
        super().__init__(*args, **kwargs)
        if user_id:       
            user = User.objects.get(id=user_id)
            
            billing_address_qs = Bill.objects.filter(
                user=user,
                address_type='B'
            )
            
            self.fields['selected_billing_address'].queryset = billing_address_qs

    def clean(self):
        data = self.cleaned_data
        
        selected_billing_address = data.get('selected_billing_address', None)
        if selected_billing_address is None:
            if not data.get('billing_address_line_1', None):
                self.add_error("billing_address_line_1", "Por favor rellena este campo")
            if not data.get('billing_address_line_2', None):
                self.add_error("billing_address_line_2", "Por favor rellena este campo")
            if not data.get('billing_zip_code', None):
                self.add_error("billing_zip_code", "Por favor rellena este campo")
            if not data.get('billing_city', None):
                self.add_error("billing_city", "Por favor rellena este campo")
        
        