import re
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.utils.http import is_safe_url
from django.views import generic
from django.conf import settings
from django.contrib.auth.models import User
from requests import request
from django.views.generic.base import View
from accounts.models import Profile, ProjectByInvestor
from projects.models import OrderItem, Pricing, Subscription, Order, SubscriptionElement, Bill, Project
from .utils import get_or_set_order_session
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib import messages
from .models import BillingProfile, Card
from django.contrib.auth.mixins import LoginRequiredMixin
from django.template.loader import render_to_string
from django.template.loader import get_template
from .utils import render_to_pdf
from django.contrib.auth.decorators import login_required
from django.db.models import F
from docxtpl import DocxTemplate
import stripe
from django.http import HttpResponse
from wsgiref.util import FileWrapper
from django.core.files import File as DjangoFile
from django.core.files import File
from pathlib import Path
from django.utils.text import slugify
import convertapi
import json
from datetime import datetime
import subprocess

# pdf



stripe.api_key = settings.STRIPE_PRIVATE_KEY

def generatePdf(request,pk):
    pdf = render_to_pdf('billing/plantilla_bill.html',pk)
    return HttpResponse(pdf, content_type='application/pdf')

class PlantillaOrderView(generic.TemplateView):
    model = Order
    template_name = 'billing/plantilla_bill.html'
    
    def get_context_data(self, *args, **kwargs):
        context = super(PlantillaOrderView, self).get_context_data(**kwargs)
        context["order"] = self.get_object()
        return context
    
    def get_object(self):
        return get_object_or_404(Order, pk = self.kwargs["pk"])
    

def generate_pdf(doc_path, path):
    subprocess.call(['soffice',
                 # '--headless',
                 '--convert-to',
                 'pdf',
                 '--outdir',
                 path,
                 doc_path])
    return doc_path



def generar_contrato(request, orden, perfil):
    factura = orden.bill
    doc = DocxTemplate("billing/templates/billing/contrato.docx")
    context = {
        'fecha': str(orden.ordered_date),
        'orden': orden.id,
        'comprador_nombre': factura.comprador_nombre, 
        'comprador_id': factura.comprador_id,
        'comprador_email': factura.comprador_email,
        'comprador_telefono': factura.comprador_phone,
        'beneficiario_nombre': factura.beneficiario_nombre, 
        'beneficiario_id': factura.beneficiario_id, 
        'beneficiario_email': factura.beneficiario_email,
        'beneficiario_telefono': factura.beneficiario_phone
        }
    doc.render(context)
    doc.save("billing/templates/billing/contrato_editado.docx")

    #doc_docx = aw.Document("billing/templates/billing/contrato_editado.docx")
    #convertapi.api_secret = settings.CONVERTAPI_SECRET_KEY
    #result = convertapi.convert('pdf', { 'File': "billing/templates/billing/contrato_editado.docx" })
    # save to file
    #result = convert("billing/templates/billing/contrato_editado.docx", "billing/templates/billing/contrato_editado.pdf" )
    #result.file.save("billing/templates/billing/contrato_editado.pdf")
    
    #doc_docx.save("billing/templates/billing/contrato_editado.pdf")
    generate_pdf("billing/templates/billing/contrato_editado.docx", "billing/templates/billing")
    path = Path("billing/templates/billing/contrato_editado.pdf")
    with path.open(mode='rb') as f:
        print(path.name)
        orden.contrato = File(f, name="contrato-%s.pdf" % (slugify(factura.comprador_nombre)))
        orden.save()
    
    
class CarteraView(generic.TemplateView):
    template_name = 'billing/cartera.html'
    
    def get_context_data(self, *args, **kwargs):
        context = super(CarteraView, self).get_context_data(**kwargs)
        orders_list  = Order.objects.filter(user=self.request.user)
        context["orders_list"] = orders_list
        return context
    

def payment_method_view(request):
    #next_url = 
    # if request.user.is_authenticated():
    #     billing_profile = request.user.billingprofile
    #     my_customer_id = billing_profile.customer_id

    billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request)
    if not billing_profile:
        return redirect("/cart")
    next_url = None
    next_ = request.GET.get('next')
    #next_ = request.GET['next']
    print(next_)
    if is_safe_url(next_, request.get_host()):
        next_url = next_
    return render(request, 'billing/payment-method.html', {"publish_key": STRIPE_PUBLIC_KEY, "next_url": next_url})

def payment_method_createview(request):
    
    if request.method == "POST" and request.is_ajax():
        print('im in create')
        billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request)
        if not billing_profile:
            return HttpResponse({"message": "Cannot find this user"}, status=401)
        token = request.POST.get("token")
        if token is not None:
            print('token is not none')
            Card.objects.add_new(billing_profile, token)
        return JsonResponse({"message": "Success! Your card was added."})
    
    return HttpResponse("error", status=401)

class CheckoutView(View):
    def get(self, request, *args, **kwargs):
        subscription =request.user.subscription

        order =  get_or_set_order_session(self.request)
        print(order.id)
        #item = order.items.all()[0]
        #pricing = get_object_or_404(Pricing, price=item.project.price.price)
        #if subscription.pricing == pricing and subscription.is_active:
        #    messages.info(request, "Actualmente ya cuentas con una suscripción activa del mismo projecto, puedes aumentar tu número de árboles por mes. ")
        #    return redirect("projects:cart")

        context={
            'order': order,
            "STRIPE_PUBLIC_KEY": settings.STRIPE_PUBLIC_KEY
        }

        #if subscription.is_active and subscription.pricing.stripe_price_id != "price_1LB5yVJUacQRIX890kzKsUYJ":
        #    return render(request, "billing/change.html", context)

        return render(request, 'billing/checkout.html', context)

def registrar_pbi(investor, project, n_trees_subscription, n_trees_one_payment):   
                print("entro a pbi")
                try:
                    obj = ProjectByInvestor.objects.get(
                        investor= investor,
                        project = project)
                    print("si existe pbi 1")
                    nts_actual = obj.n_trees_subscription
                    nto_actual = obj.n_trees_one_payment
                    obj.n_trees_subscription = nts_actual + n_trees_subscription
                    obj.n_trees_one_payment = nto_actual + n_trees_one_payment
                    print("si existe pbi")
                    obj.save()
                    
                except ProjectByInvestor.DoesNotExist:
                    print(f"investor: {investor} y project: {project}" )
                    obj = ProjectByInvestor.objects.create(
                        investor= investor,
                        project = project, 
                        n_trees_subscription = n_trees_subscription,
                        n_trees_one_payment = n_trees_one_payment
                    )
                    print("no existe pbi")
                    
                    obj.save() 
            
def registrar_pbi_sus(investor, project, n_trees_subscription, n_trees_one_payment):   
                try:
                    obj = ProjectByInvestor.objects.get(
                        investor= investor,
                        project = project)
                    nto_actual = obj.n_trees_one_payment
                    obj.n_trees_subscription = n_trees_subscription
                    obj.n_trees_one_payment = nto_actual + n_trees_one_payment
                    obj.save()
                    
                except ProjectByInvestor.DoesNotExist:
                    obj = ProjectByInvestor.objects.create(
                        investor= investor,
                        project = project
                    )
                    obj.n_trees_subscription = n_trees_subscription
                    obj.n_trees_one_payment = n_trees_one_payment
                    obj.save()  

class CreateSubscriptionView(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        profile = get_object_or_404(Profile, user_id=request.user.id)
        customer_id = profile.stripe_customer_id
        orden =  get_or_set_order_session(self.request)
        
        try:
            #vincular el metodo de pago al cliente
            stripe.PaymentMethod.attach(
                data['paymentMethodId'],
                customer=customer_id
            )

            #configuurar metodo de pago prederterminado del cliente
            iss= stripe.Customer.modify(
                customer_id,
                invoice_settings={
                    'default_payment_method': data['paymentMethodId'],
                },
            )
            
            ## Buscamos el Project By investor o lo creamos
              
            ## pagos unicos
            mis_cantidades = {}
            for item in orden.items.filter(type_inversion = 'O'):
                mis_cantidades[item.project.price_onepayment.stripe_price_id] = item.quantity 
                mis_precios = list(mis_cantidades.keys())
                item.project.trees_left-= item.quantity
                print(item.project.trees_left)
                item.project.save()
                print(item.project.trees_left)
                registrar_pbi(request.user, item.project, 0, item.quantity)
                print("registró pbi en pago único")
            
            
            for item in list(mis_cantidades.keys()): 
                domain_url = settings.DOMINIO_URL  
                #session = create_checkout_session(item, mis_cantidades, customer_id)
                try:
                    # Create a git  with the order amount and currency
                    monto = Pricing.objects.filter(stripe_price_id=item)[0].price * mis_cantidades[item]
                    print("creó monto final para item pago unico")
                    intent = stripe.PaymentIntent.create(
                        amount= monto,
                        currency='usd',
                        customer=customer_id,
                        metadata = {
                            'price': item,
                            'quantity': mis_cantidades[item],   
                        },
                        automatic_payment_methods={
                            'enabled': True,
                        },
                    )
                    stripe.PaymentIntent.confirm(
                        intent.id,
                        payment_method=data['paymentMethodId'],
                       
                        return_url= domain_url + '/billing/success/',
                    )
                except Exception as e:
                    print(str(e))
                    

            #crear suscripcion
            datasub = {}
            datach = {}
            subscription = request.user.subscription
            stripe_subscription = stripe.Subscription.retrieve(subscription.stripe_subscription_id)
            estado_actual = stripe_subscription.status
            mis_cantidades = {}
            mis_proyectos = {}
            
            items_existentes = stripe.SubscriptionItem.list(
                subscription = stripe_subscription.id
            )
            
            if estado_actual == 'trialing':
                stripe_subscription = stripe.Subscription.modify(
                    subscription.stripe_subscription_id,
                    trial_end="now",
                )
                subscription.status=stripe_subscription.status
                subscription.save()  
            
            
            
            ## Creamos un diccionario de los productos segun codigo de precio y cantidad
            ## Creamos un diccionario de los productos segun codigo de precio y su proyecto
            for item in orden.items.filter(type_inversion = 'M'):
                mis_cantidades[item.project.price_subscription.stripe_price_id] = item.quantity
                mis_proyectos[item.project.price_subscription.stripe_price_id] =  item.project
                #registrar_pbi(request.user, item.project, item.quantity, 0)
            
            # Busca subscription Item o por el contrario la crea
            subidos= []
            mis_precios = list(mis_cantidades.keys())
                        
            for item in items_existentes:  
                if item['price']["id"] in mis_precios:  
                    new_quantity = mis_cantidades[item['price']["id"]]
                    actual_quantity = item['quantity']
                    stripe.SubscriptionItem.modify(
                        item.id,
                        quantity= actual_quantity + new_quantity,
                        proration_behavior='always_invoice',
                        metadata={'order_id': orden.id,
                                'user': request.user.id},
                    )    
                    subidos.append(item['price']["id"])
            
            for k in subidos:
                mis_cantidades.pop(k)
            for item in list(mis_cantidades.keys()): 
                stripe.SubscriptionItem.create(
                    subscription=stripe_subscription.id,
                    price= item,
                    proration_behavior='always_invoice',
                    quantity= mis_cantidades[item],
                    metadata={'order_id': orden.id,
                            'user': request.user.id
                            },
                )
            
            if len(orden.items.filter(type_inversion = 'M')) > 0:
                for item in items_existentes:  
                    if item['price']["id"] == settings.STRIPE_FREE_PRICE:
                            stripe.SubscriptionItem.delete(
                                item['id']
                            )
            
            datasub.update(stripe_subscription)
            data= [datasub, datach]
            generar_contrato(request, orden, profile)
            return Response(data)
        except Exception as e:
            return Response({
                "error": {'message': str(e)}
            })

class RetryInvoiceView(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        profile = Profile.objects.get(user_id=request.user.id)
        customer_id = profile.profile.stripe_customer_id
        
        try:

            stripe.PaymentMethod.attach(
                data['paymentMethodId'],
                customer=customer_id,
            )
            # Set the default payment method on the customer
            stripe.Customer.modify(
                customer_id,
                invoice_settings={
                    'default_payment_method': data['paymentMethodId'],
                },
            )

            invoice = stripe.Invoice.retrieve(
                data['invoiceId'],
                expand=['payment_intent'],
            )
            data = {}
            data.update(invoice)

            return Response(data)
        except Exception as e:

            return Response({
                "error": {'message': str(e)}
            })

class ChangeSubscriptionView(APIView):
    def post(self, request, *args, **kwargs):
        
        subscription_id = request.user.subscription.stripe_subscription_id
        subscription = stripe.Subscription.retrieve(subscription_id)
        try:
            updatedSubscription = stripe.Subscription.modify(
                subscription_id,
                cancel_at_period_end=False,
                items=[{
                    'id': subscription['items']['data'][0].id,
                    'price': request.data["priceId"],
                }],
                proration_behavior="none"
            )

            data = {}
            data.update(updatedSubscription)
            return Response(data)
        except Exception as e:
            return Response({
                "error": {'message': str(e)}
            })

class PaymentSuccessView(generic.TemplateView):
    
    template_name = "billing/success.html"
    
    def get_context_data(self, *args, **kwargs):
            context = super(PaymentSuccessView, self). get_context_data(**kwargs)
            order =  get_or_set_order_session(self.request)
            print("successs View")
            print(order.id)
            order.ordered = True
            order.save()
            context["order"] = order
            self.request.session['order_id'] = None
            return context
        
class PaymentCancelledView(generic.TemplateView):
    template_name = "billing/cancelled.html"
 
class PaymentFailedView(generic.TemplateView):
    template_name = "billing/failed.html"
    def get_context_data(self, *args, **kwargs):
        context = super(PaymentFailedView, self). get_context_data(**kwargs)
        context["order"] = get_or_set_order_session(self.request)
        #self.request.session['order_id'] = None
        return context

class OrderHistoryListView(generic.TemplateView):
    pass

@csrf_exempt
def webhook(request):
  payload = request.body
  event = None

  try:
    event = stripe.Event.construct_from(
      json.loads(payload), stripe.api_key
    )
  except ValueError as e:
    # Invalid payload
    return HttpResponse(status=400)

  # Handle the event
  if event.type == 'payment_intent.succeeded':
    print("entro a webhook intent succeded")
    #payment_intent = event.data.object # contains a stripe.PaymentIntent
    # Then define and call a method to handle the successful payment intent.
    # handle_payment_intent_succeeded(payment_intent)
  elif event.type == 'payment_method.attached':
    payment_method = event.data.object # contains a stripe.PaymentMethod
    # Then define and call a method to handle the successful attachment of a PaymentMethod.
    # handle_payment_method_attached(payment_method)
  elif event.type == 'customer.subscription.updated':
    objeto = event.data.object
    print("Suscripcion ha sido cambiada")
    
    previo = event.data.previous_attributes
    es_solo_activacion = False
    if 'status' in previo:
        if previo['status'] == "trialing" and objeto['status']:
            es_solo_activacion = True

    if not es_solo_activacion:
        if 'items' in previo:
            ## Osea se compro manualmente
            print("entro a un cambio de suscripcion en uno de los items")
            
            items = objeto['items']['data']
            print(len(items))
            precios = []
            for item in items:
                precios.append(item['price']["id"])
            if settings.STRIPE_FREE_PRICE not in precios:
                for item in items:
                    ## Subscripcion local
                    subscription = get_object_or_404(Subscription, stripe_subscription_id=objeto['id'])
                    print(settings.STRIPE_FREE_PRICE)
                    print(item['price']["id"])
                    if 'order_id' in item['metadata'] and item['price']["id"] != settings.STRIPE_FREE_PRICE:
                        mis_cantidades = {}
                        mis_proyectos = {}
                        print(item)
                        user = get_object_or_404(User, pk=item['metadata']['user'])
                        orden = get_object_or_404(Order, pk=item['metadata']['order_id'])
                        order_item = orden.items.filter(type_inversion = 'M').filter(project__price_subscription__stripe_price_id=item['price']['id'])[0]
                        
                        proj = order_item.project
                        print(proj.trees_left)
                        proj.trees_left -= order_item.quantity
                        proj.save()
                        print(proj.trees_left)
                        registrar_pbi_sus(user, order_item.project, item['quantity'], 0)
                        
                        precio_loc = get_object_or_404(Pricing, stripe_price_id= item['price']['id'])
                        
                        try:  
                            element = SubscriptionElement.objects.get(
                                subscription = subscription,
                                price= precio_loc)
                        
                        except SubscriptionElement.DoesNotExist:
                            element = SubscriptionElement.objects.create(
                                subscription = subscription,
                                price= precio_loc,
                                project = order_item.project,
                                quantity = 0)
                            element.save()
                        
                        
                        new_quantity_loc = item['quantity']
                        element.quantity = new_quantity_loc
                        element.save()
        else:
            print("entró a recurrente")
            user_stripe_id = objeto['customer']
            perfil = get_object_or_404(Profile, stripe_customer_id = user_stripe_id)
            user = perfil.user
        
            items = objeto['items']['data']
            
           
            order = Order()
            order.ordered_date = datetime.now()
            order.user = user
            order.save()
            for item in items:
                precio_id = item['price']['id']
                precio = get_object_or_404(Pricing, stripe_price_id=precio_id )
                project = Project.objects.filter(price_subscription = precio)  
                project[0].trees_left -= item['quantity']
                project[0].save()
                order_item = OrderItem()
                order_item.order = order
                order_item.project = project[0]
                order_item.quantity = item['quantity']
                order_item.type_inversion = 'M'
                order_item.save()
                
                registrar_pbi(user, order_item.project, order_item.quantity, 0)
            
            if not order.items:
                order.delete()
            else:
                order.ordered= True
                order.save()
    
  elif event.type == 'invoiceitem.created':
      print("Se creó un invoiceitem")
  
  elif event.type == 'invoiceitem.updated':
      print("actualizó un invoiceitem")
     
  elif event.type == 'invoice.paid':
      print("La factura se paga correctamente.")
  else:
    print('Unhandled event type {}'.format(event.type))

  return HttpResponse(status=200)

@csrf_exempt
def stripe_config(request):
    if request.method == 'GET':
        stripe_config = {'publicKey': settings.STRIPE_PUBLIC_KEY}
        return JsonResponse(stripe_config, safe=False)

@csrf_exempt
def create_checkout_session(item, mis_cantidades, customer_id):
    domain_url = settings.DOMINIO_URL
    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                    {
                    'price': item,
                    'quantity': mis_cantidades[item],
                    
                    },
                ],
                mode='payment',
                payment_method_types=['card',],
                customer=customer_id,
                success_url=domain_url + '/billing/success/',
                cancel_url=domain_url + '/billing/cancelled/',
        )
        return checkout_session
    except Exception as e:
        return JsonResponse({'error': str(e)})