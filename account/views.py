from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.shortcuts import HttpResponse
from django.contrib import auth
from django.contrib.auth import authenticate,login
from django.contrib.auth.models import User
from django.template.context_processors import csrf
from .forms import LoginForm, UserRegistrationForm,UserEditForm,ProfileEditForm
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.template import RequestContext
import hashlib, datetime, random
from .models import *
from django.contrib import messages
from django.utils import timezone
from django.utils.encoding import force_bytes, force_str
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .token_generator import account_activation_token
from django.core.mail import EmailMessage
from rolepermissions.roles import assign_role



def home(request):
    return render(request,'account/index.html',{'section':'index'})

@login_required
def dashboard(request):
    return render(request,'account/dashboard.html',{'section':'dashboard'})

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request,username=cd['username'],
                                      password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request,user)
                    return HttpResponse('Authenticated'' Successfully')
                else:
                    return HttpResponse('Disabled Account')
            else:
                return HttpResponse("Invalid login")
    else:
        form=LoginForm()
    return render(request,'account/login.html',{'form':form})

def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.is_active = False
            new_user.set_password(user_form.cleaned_data['password'])
            user_form.save()  # guardar el usuario en la base de datos si es válido


            # Enviar un email de confirmación
            current_site = get_current_site(request)
            email_subject = 'Activate Your Account'
            message = render_to_string('registration/activate_account.html', {
                'user': new_user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(new_user.pk)),
                'token': account_activation_token.make_token(new_user),
            })
            to_email = user_form.cleaned_data.get('email')
            email = EmailMessage(email_subject, message, to=[to_email])
            email.send()
            #return HttpResponse('We have sent you an email, please confirm your email address to complete registration')
            return render(request,'registration/confirm_account.html')
            

            
    else:
        user_form=UserRegistrationForm()
    return render(request,'account/register.html',{'user_form': user_form})
    
def activate_account(request, uidb64, token, backend='django.contrib.auth.backends.ModelBackend'):
    try:
        uid = force_bytes(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        #return HttpResponse('Your account has been activate successfully')
        # Crear el perfil del usuario 
        if not user.profile:
          new_profile = Profile(user=user)
          new_profile.save()
        # Asigna rol inversioniste
        assign_role(user, 'inversor')
        return render(request,'account/register_done.html',{'new_user': user})
    else:
        return HttpResponse('Activation link is invalid!')


@login_required
def edit(request):
    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user,data=request.POST)
        profile_form = ProfileEditForm(instance=request.user.profile,
                                       data=request.POST,files=request.FILES)
        #import pdb; pdb.set_trace()
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('profile')
        else:
            messages.error(request, 'Error in Updating your Profile.')
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)
        #import pdb; pdb.set_trace()
    return render(request,'account/edit.html',{'user_form':user_form,'profile_form':profile_form, 'user': request.user})

@login_required
def profile(request):
    return render(request,'account/profile.html', {'user': request.user})