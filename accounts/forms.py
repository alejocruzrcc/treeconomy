from django import forms
from django.contrib.auth.models import User
from .models import Profile
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from .models import ProjectByInvestor
from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.widgets import PhoneNumberPrefixWidget
from django.contrib.auth.forms import AuthenticationForm, UsernameField



class UserPasswordResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super(UserPasswordResetForm, self).__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data['email']
        if not User.objects.filter(email__iexact=email, is_active=True).exists():
            msg = ("No hay un usuario registrado con este correo electrónico")
            self.add_error('email', msg)
        return email
   

    email = forms.EmailField(label='', widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Correo Electrónico',
        'type': 'email',
        'name': 'Correo Electrónico'
        }))
    


class UserPasswordResetConfirmForm(SetPasswordForm):

    new_password1 = forms.CharField(label='', widget=forms.PasswordInput(attrs={
        'class': 'form-control my-2',
        'placeholder': 'Nueva contraseña',
        'type': 'password',
        'name': 'Nueva contraseña'
        }))

    new_password2 = forms.CharField(label='', widget=forms.PasswordInput(attrs={
        'class': 'form-control my-2',
        'placeholder': 'Confirme nueva contraseña',
        'type': 'password',
        'name': 'Confirme nueva contraseña'
        }))


class LoginForm(AuthenticationForm):
    username = UsernameField(
        label='Team Name'
    )

class UserRegistrationForm(forms.ModelForm):
    username=forms.CharField(label='Nombre de usuario')
    first_name=forms.CharField(label='Nombres')
    last_name=forms.CharField(label='Apellidos')
    email=forms.CharField(label='Correo electrónico')
    password=forms.CharField(label='Contraseña',widget=forms.PasswordInput)
    password2=forms.CharField(label='Confirma contraseña',widget=forms.PasswordInput)

    class Meta:
        model=User
        fields = ('username','first_name', 'last_name', 'email')

    def clean_password2(self):
        cd=self.cleaned_data
        if cd['password']!=cd['password2']:
            raise forms.ValidationError('Contraseñas no coinciden')
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
    def __init__(self, *args, **kwargs):
        super(UserEditForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'

class ProfileEditForm(forms.ModelForm):
    phone= PhoneNumberField(
        widget=PhoneNumberPrefixWidget(attrs={'placeholder': (u'Número de Teléfono'), 'class': "form-control"}),
        label='Comprador teléfono',
        required=False,
        initial='+57'
    )
    date_of_birth = forms.DateField(widget=forms.widgets.DateInput(attrs={"type": "date"}))
    class Meta:
        model = Profile
        fields = '__all__'
        exclude = ['user', 'stripe_customer_id']
        
    def __init__(self, *args, **kwargs):
        super(ProfileEditForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'

class ContactForm(forms.Form):
    
    name = forms.CharField(label="Nombre",  max_length=100, widget=forms.TextInput(attrs={

        'placeholder': "Nombre"
        
    }))    
    email = forms.EmailField(label="Correo", widget=forms.TextInput(attrs={
        'placeholder': "Correo"
    }))
    phone = PhoneNumberField(label="Telefono", widget=forms.TextInput(attrs={
        'placeholder': "Telefono"
    }))  
    message = forms.CharField(label="Mensaje", widget=forms.TextInput(attrs={
        
        'placeholder': "Escribenos"
    }))
    
class PasswordChangeForm(SetPasswordForm):
    """
    A form that lets a user change their password by entering their old
    password.
    """

    #old_password=forms.CharField(label='Actual contraseña',widget=forms.PasswordInput)
    new_password1=forms.CharField(label='Nueva contraseña',widget=forms.PasswordInput)
    new_password2=forms.CharField(label='Confirma contraseña',widget=forms.PasswordInput)

    error_messages = dict(SetPasswordForm.error_messages, **{
        'password_incorrect': ("Your old password was entered incorrectly. "
                                "Please enter it again."),
    })
    old_password = forms.CharField(label= ("Old password"),
                                   widget=forms.PasswordInput)

    def clean_old_password(self):
        """
        Validates that the old_password field is correct.
        """
        old_password = self.cleaned_data["old_password"]
        if not self.user.check_password(old_password):
            raise forms.ValidationError(
                self.error_messages['password_incorrect'],
                code='password_incorrect',
            )
        return old_password


