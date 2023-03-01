from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.shortcuts import HttpResponse, reverse
from django.contrib import auth
from django.contrib.auth import authenticate,login, logout
from django.contrib.auth.views import PasswordResetView 
from django.contrib.auth.models import User
from django.template.context_processors import csrf
from django.conf import settings
from projects.forms import ProjectByInvestorForm
from .forms import LoginForm, UserRegistrationForm,UserEditForm,ProfileEditForm, ContactForm, CompanyForm
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.template import RequestContext
import hashlib, datetime, random
from .models import *
from projects.models import Order, OrderItem
from django.contrib import messages
from django.utils import timezone
from django.utils.encoding import force_bytes, force_str
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .token_generator import account_activation_token
from django.core.mail import EmailMessage
from rolepermissions.roles import assign_role, remove_role, get_user_roles
from django.core import serializers
from django.http import JsonResponse
from django.views import generic
from rolepermissions.decorators import has_role_decorator
from dashboard.views import invest_json, calculo_co2
import stripe
import xlwt
from django.http import HttpResponse
from django.contrib.auth.models import User
from datetime import datetime
import pandas as pd
import qrcode
from rolepermissions.mixins import HasRoleMixin
from django.utils.text import slugify
from django.core.files import File
from django.contrib.auth.mixins import LoginRequiredMixin


stripe.api_key = settings.STRIPE_PRIVATE_KEY

def calculadora(request):
    return render(request,'account/calculadora.html',{'section':'calculadora'})

class ContactView(generic.FormView):
    form_class = ContactForm
    template_name = "account/contact.html"
    
    def get_success_url(self):
        return reverse("contact")
    
    def form_valid(self, form):
        messages.info(self.request, "Hemos recibido tu mensaje")
        name = form.cleaned_data.get('name')
        email = form.cleaned_data.get('email')
        message = form.cleaned_data.get('message')
        phone = form.cleaned_data.get('phone')
        
        full_message = f"""
            
            Mensaje recibido de {name}, {email}, {phone}
            ------------------------------------
            
            {message}
            """
        send_mail(
            subject="Mensaje recibido por contact form",
            message=full_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.NOTIFY_EMAIL]
        )
        return super(ContactView, self).form_valid(form)
        
    

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

def user_logout(request):
    logout(request)
    video_idea_negocio = get_object_or_404(Video, nombre="idea_negocio")
    return render(request,'registration/logged_out.html', {'video_idea_negocio': video_idea_negocio})

def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.is_active = False
            new_user.set_password(user_form.cleaned_data['password'])
            print(user_form.cleaned_data)
            user_form.save()  # guardar el usuario en la base de datos si es válido
            # Enviar un email de confirmación
            current_site = get_current_site(request)
            email_subject = 'Confirma tu registro en Treeconomy Inc.'
            message = render_to_string('registration/activate_account.html', {
                'user': new_user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(new_user.pk)),
                'token': account_activation_token.make_token(new_user),
            })
            to_email = user_form.cleaned_data.get('email')
            email = EmailMessage(email_subject, message, to=[to_email])
            email.content_subtype = "html"
            email.send()
            if not new_user.profile:
                new_profile = Profile(user=new_user)
            else: 
                new_profile = new_user.profile

            is_company = user_form.cleaned_data['is_company']
            
            if is_company:
                new_profile.tipocliente = 2
                company_name = user_form.cleaned_data['company_name']
                company = Company(user=new_user, slug=slugify(company_name), name=company_name)
                company.save()
                assign_role(new_user, 'company')
            else:
                new_profile.tipocliente = 1
                # Asigna rol inversioniste
                assign_role(new_user, 'inversor')
            new_profile.save()
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
        
        
        video_idea_negocio = get_object_or_404(Video, nombre="idea_negocio")
        
        return render(request,'account/register_done.html',{'new_user': user, 'video_idea_negocio': video_idea_negocio})
    else:
        return HttpResponse('Activation link is invalid!')


@login_required
def edit(request):
    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user,data=request.POST)
        profile_form = ProfileEditForm(instance=request.user.profile,
                                       data=request.POST,files=request.FILES)
        #profile_form.data['stripe_customer_id'] = request.user.profile.stripe_customer_id
        #import pdb; pdb.set_trace()
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('profile')
        else:
            messages.error(request, user_form.errors)
            messages.error(request, profile_form.errors)
            
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)
        #import pdb; pdb.set_trace()
    return render(request,'account/edit.html',{'user_form':user_form,'profile_form':profile_form, 'user': request.user})

@login_required
def profile(request):
    user = request.user
    total = user.profile.get_total_trees
    inversion = user.profile.get_inversion
    ## Utilidad
    invest = invest_json(request)
    resumen = invest[1]
    suma_utilidad = 0
    suma_arboles_acumulados = 0
    co2_consumption = calculo_co2(request)
    
    ## Suscripciones
    subscription = get_object_or_404(Subscription, user=request.user)
    if subscription:
        elementos = SubscriptionElement.objects.filter(subscription=subscription)
    
    for key in resumen:
        suma_utilidad += float(resumen[key]['utilidad'])
        suma_arboles_acumulados += resumen[key]['total_trees']
    #co2_capturado = CO2_CONSUMPTION_PER_TREE_PER_DAY * suma_arboles_acumulados * 365
    suma_utilidad_str = "{:.2f}".format(suma_utilidad)

    return render(request,'account/profile.html', {
        'user': request.user, 
        'total': total, 
        'inversion': inversion,
        'utilidad': suma_utilidad_str,
        'co2_capturado': co2_consumption, 
        'elementos': elementos,
        })


class ModifySubscriptionElement(generic.View):
    def get(self, request, *args, **kwargs):    
        subscription = get_object_or_404(Subscription, user=request.user)
        price = get_object_or_404(Pricing, pk=kwargs['pk'])
        try: 
            selem = SubscriptionElement.objects.get(subscription=subscription, price=price)
            items_existentes = stripe.SubscriptionItem.list(
                    subscription = subscription.stripe_subscription_id
                )
            for item in items_existentes:
                if item['price']["id"] == price.stripe_price_id:
                    stripe.SubscriptionItem.delete(
                    item.id,
                )
            selem.delete()
        except:
            print("No fue posible cancelar la suscripción")
        
        return redirect("/account/profile")

class PauseSubscriptionElement(generic.View):
    def get(self, request, *args, **kwargs):    
        subscription = get_object_or_404(Subscription, user=request.user)
        price = get_object_or_404(Pricing, pk=kwargs['pk'])
        try: 
            selem = SubscriptionElement.objects.get(subscription=subscription, price=price)
            items_existentes = stripe.SubscriptionItem.list(
                    subscription = subscription.stripe_subscription_id
                )
            for item in items_existentes:
                if item['price']["id"] == price.stripe_price_id:
                    stripe.SubscriptionItem.delete(
                    item.id,
                )
            selem.delete()
        except:
            print("No fue posible cancelar la suscripción")
        
        return redirect("/account/profile")

class UserListView(HasRoleMixin, generic.TemplateView):
    allowed_roles = 'admin'
    model = User
    template_name = 'account/users.html'

    
    def get_context_data(self, *args, **kwargs):
        context = super(UserListView, self).get_context_data(*args, **kwargs) 
        context['usuarios'] = User.objects.all().order_by('-date_joined')     
        return context

@has_role_decorator('admin')   
def export_clients_xls(request):
    response = HttpResponse(content_type='application/ms-excel')
    today = datetime.today().date()
    response['Content-Disposition'] = f'attachment; filename="clientes-{today}.xls"'
    
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Users Data') # this will make a sheet named Users Data

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['Usuario', 'Nombres', 'Apellidos', 'Correo', "Teléfono", 'Total Árboles', 'Inversión' ]

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style) # at 0 row 0 column 

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()

    rows = User.objects.all().values_list('username', 'first_name', 'last_name', 'email')
    users = User.objects.all()
    data = []
    
    for user in users:
        if Profile.objects.filter(user=user).exists():
            data.append([user.username, user.first_name, user.last_name, user.email, str(user.profile.phone), str(user.profile.get_total_trees()), str(user.profile.get_inversion())])
        else:
            data.append([user.username, user.first_name, user.last_name, user.email, "Usuario sin perfil", "Usuario sin perfil", "Usuario sin perfil"])
    df = pd.DataFrame(data, columns=columns)
    
    for index, row in df.iterrows():
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)

    return response
    
@has_role_decorator('admin')   
def export_clients_pag(request):
    users = User.objects.all()
    data = []
    
    for user in users:
        if Profile.objects.filter(user=user).exists():
            data.append([user.username, user.first_name, user.last_name, user.email, user.profile.phone, str(user.profile.get_total_trees()), str(user.profile.get_inversion())])
        else:
            data.append([user.username, user.first_name, user.last_name, user.email, "Usuario sin perfil", "Usuario sin perfil", "Usuario sin perfil"])
    
    return render(request,'account/clientes.html', {
            'data': data, 
            })
    
@has_role_decorator('admin')   
def export_orders_xls(request):
    response = HttpResponse(content_type='application/ms-excel')
    today = datetime.today().date()
    response['Content-Disposition'] = f'attachment; filename="orders-{today}.xls"'
    
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Users Data') # this will make a sheet named Users Data

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['Id', 'Date', 'Lote', 'Cantidad', 'Precio Unitario', 'Total', 'Status', 'Inversion Type', 'First Name', 'Last Name', 'Customer email', 'Ciudad', 'Año', 'Mes']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style) # at 0 row 0 column 

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()

    orderitems = OrderItem.objects.all()
    data = []
    
    for item in orderitems:
        order = item.order
        if order.user:
            data.append([order.id, str(order.ordered_date) if order.ordered_date else "Sin fecha", item.project.name, item.quantity, f"${item.project.get_price()}", item.get_total_item_price(), order.get_status(), item.get_type_inversion_display(), str(order.user.first_name), str(order.user.last_name), str(order.user.email), str(order.user.profile.city), order.ordered_date.strftime('%Y') if order.ordered_date else '', order.ordered_date.strftime('%b') if order.ordered_date else ''])
   
    df = pd.DataFrame(data, columns=columns)
    
    for index, row in df.iterrows():
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)

    return response

@has_role_decorator('admin')      
def export_orders_pag(request):
    columns = ['Id', 'Date', 'Lote', 'Cantidad', 'Precio Unitario', 'Total', 'Status', 'Inversion Type', 'First Name', 'Last Name', 'Customer email', 'Ciudad', 'Año', 'Mes']
    
    # Sheet body, remaining rows
    orderitems = OrderItem.objects.all()
    data = []
    
    for item in orderitems:
        order = item.order
        if order.user:
            data.append([order.id, str(order.ordered_date) if order.ordered_date else "Sin fecha", item.project.name, item.quantity, f"${item.project.get_price()}", item.get_total_item_price(), order.get_status(), item.get_type_inversion_display(), str(order.user.first_name), str(order.user.last_name), str(order.user.email), str(order.user.profile.city), order.ordered_date.strftime('%Y') if order.ordered_date else '', order.ordered_date.strftime('%b') if order.ordered_date else ''])
   
    
    return render(request,'account/ordenes.html', {
            'columns': columns,
            'data': data, 
            })

def manageqr(request):
    companies = Company.objects.filter(user= request.user)
    print(companies.count())
    if companies.count() > 0:
        company = companies[0]
        return render(request, "qrcode/manageqr.html", {'company': company, 'is_company': True})
    else:
        return render(request, "qrcode/manageqr.html", {'is_company': False})
    
def create_company(request):
    company_instance = Company(user= request.user)

    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = CompanyForm(request.POST or None, request.FILES or None, instance=company_instance)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            company_instance.slug = slugify(form.cleaned_data['name'])
            company_instance.save()
            role = get_user_roles(request.user)
            print(role)
            remove_role(request.user, 'inversor')
            assign_role(request.user, 'company')
            # redirect to a new URL:
            return HttpResponseRedirect(reverse('manageqr'))
    else:
        form = CompanyForm(request.POST or None, request.FILES or None)

    return render(request, "qrcode/create_company.html", {'formulario': form})

@has_role_decorator('company')
def edit_company(request, pk):
    company = Company.objects.get(pk=pk)
    formulario = CompanyForm(request.POST or None, request.FILES or None, instance=company)
    
    if formulario.is_valid() and request.POST:
        #company.logotipo.delete()
        #company.portadas.delete()  # This will delete your old image
        formulario.save()
        return redirect('/account/managecode')
    else:
        errores = formulario.errors

    return render(request, "qrcode/edit_company.html", {'formulario': formulario, 'errores': errores})


@has_role_decorator('company')
def createqr(request):
    companies= Company.objects.filter(user=request.user)
    if companies.count() == 1:
        company= companies[0]
        is_company = True
        input = f'{settings.PROTOCOLO}://app.treeconomy.com.co/dashboard/companies/{company.slug}'
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(input)
        qr.make(fit=True)    
        img = qr.make_image(fill='black', back_color='white')
        ruta = f'{settings.MEDIA_ROOT}qrcodes/{company.slug}.png'
        img.save(ruta)
            
        company.qrcode.save(f'qrcodes/{company.slug}.png', File(open(ruta, 'rb')))
        company.save()
        return render(request,'qrcode/manageqr.html', {
        'company': company,
        'is_company': is_company 
        })
    else:
        is_company = False
        return render(request,'qrcode/manageqr.html', {
        'is_company': is_company 
        })
    
    
            