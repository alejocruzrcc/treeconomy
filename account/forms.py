from django import forms
from django.contrib.auth.models import User
from .models import Profile
from django.contrib.auth.forms import PasswordResetForm
from .models import Subscription, ProjectByInvestor
OPTIONS = (('Active', 'Active'), ('Closed', 'Closed'), ('On hold', 'On hold'))

class EmailValidationOnForgotPassword(PasswordResetForm):

    def clean_email(self):
        email = self.cleaned_data['email']
        if not User.objects.filter(email__iexact=email, is_active=True).exists():
            msg = ("There is no user registered with the specified E-Mail address.")
            self.add_error('email', msg)
        return email

class LoginForm(forms.Form):
    username= forms.CharField()
    password=forms.CharField(widget=forms.PasswordInput)

class UserRegistrationForm(forms.ModelForm):
    password=forms.CharField(label='Password',widget=forms.PasswordInput)
    password2=forms.CharField(label='Repeat Password',widget=forms.PasswordInput)

    class Meta:
        model=User
        fields = ('username','first_name', 'last_name', 'email')

    def clean_password2(self):
        cd=self.cleaned_data
        if cd['password']!=cd['password2']:
            raise forms.ValidationError('Passwords don\'t Match')
        return cd['password2']
    #clean email field
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            if User.objects.filter(email=email).exists():
                raise forms.ValidationError('This email address is unavailable!')
            else:
                pass
        return email
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in ['username', 'first_name', 'last_name', 'email', 'password', 'password2']:
            self.fields[field].widget.attrs['class'] = 'form-control form-control-lg'

class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name','last_name','email')

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = '__all__'

class SubscriptionForm(forms.ModelForm):
    status = forms.ChoiceField(choices=OPTIONS, required=True) 

    class Meta:
        model = Subscription
        fields = ('investor', 'current_payment', 'next_payment', 'status', 'total', 'start_date', 'last_order_date', 'n_projects')
    
    def clean_status(self):
        status = self.cleaned_data['status']
        if not status:
            raise forms.ValidationError('You have to provide a status for this subscription')
        
        return status




