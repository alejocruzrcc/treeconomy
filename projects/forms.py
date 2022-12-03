from django.forms import ModelForm 
from django.urls import reverse
from django import forms
from .models import OrderItem, Project, Bill, Subscription, Vendedor
from accounts.models import ProjectByInvestor, User
from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.widgets import PhoneNumberPrefixWidget

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
        for field in ['type_inversion']:
            self.fields[field].widget.attrs['class'] = 'form-select'
        
class SubscriptionForm(forms.ModelForm):
    OPTIONS = (('Active', 'active'), ('Closed', 'closed'), ('On hold', 'On hold'))
    status = forms.ChoiceField(choices=OPTIONS, required=True) 

    class Meta:
        model = Subscription
        fields = ('user', 'n_projects')
    
    def clean_status(self):
        status = self.cleaned_data['status']
        if not status:
            raise forms.ValidationError('Tienes que especificar un estado para esta suscripción.')
        
        return status

class BillForm(forms.Form):
    error_css_class = 'is-invalid'
    comprador_nombre = forms.CharField(label="Nombre completo")
    comprador_id = forms.CharField(label="Identificación")
    comprador_email = forms.EmailField(label="Correo electrónico")
    comprador_phone = PhoneNumberField(
        widget=PhoneNumberPrefixWidget(attrs={'placeholder': (u'Número de Teléfono'), 'class': "form-control"}),
        label='Teléfono',
        required=False,
        initial='+57'
    )
    beneficiario_nombre = forms.CharField(label="Nombre completo", required=False)
    beneficiario_id = forms.CharField(label="Identificación", required=False)
    beneficiario_email = forms.EmailField(label="Correo electrónico", required=False)
    beneficiario_phone =  PhoneNumberField(
        widget=PhoneNumberPrefixWidget(attrs={'placeholder': (u'Número de Teléfono'), 'class': "form-control"}),
        label='Teléfono',
        required=False,
        initial='+57'
    )  
    billing_address_line_1 = forms.CharField(label="Dirección")
    billing_address_line_2 = forms.CharField(label="Casa, Apartamento, etc.")
    billing_zip_code = forms.CharField(label="Código postal")
    billing_city = forms.CharField(label="Ciudad")
    
    vendedor = forms.ModelChoiceField(queryset=Vendedor.objects.all(), required=False)
      
    def __init__(self, *args, **kwargs):
        user_id = kwargs.pop('user_id')
        super().__init__(*args, **kwargs)
        if user_id:       
            user = User.objects.get(id=user_id)
            
            billing_address_qs = Bill.objects.filter(
                user=user,
                address_type='B'
            )
            
            #self.fields['selected_billing_address'].queryset = billing_address_qs
        
        