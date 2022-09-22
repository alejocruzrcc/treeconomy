import re
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.utils.http import is_safe_url
from django.views import generic
from django.conf import settings
from requests import request
from django.views.generic.base import View
from accounts.models import Profile, ProjectByInvestor
from projects.models import OrderItem, Pricing, Subscription, Order, SubscriptionElement, Bill
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
    
def generar_contrato(request, orden, perfil):
    factura = orden.bill
    doc = DocxTemplate("billing/templates/billing/contrato.docx")
    context = {
        'fecha': orden.ordered_date,
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
    convertapi.api_secret = settings.CONVERTAPI_SECRET_KEY
    result = convertapi.convert('pdf', { 'File': "billing/templates/billing/contrato_editado.docx" })
    # save to file
    result.file.save("billing/templates/billing/contrato_editado.pdf")
    
    #doc_docx.save("billing/templates/billing/contrato_editado.pdf")
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
            def registrar_pbi(investor, project, n_trees_subscription, n_trees_one_payment):   
                try:
                    obj = ProjectByInvestor.objects.get(
                        investor= investor,
                        project = project)
                    nts_actual = obj.n_trees_subscription
                    nto_actual = obj.n_trees_one_payment
                    obj.n_trees_subscription = nts_actual + n_trees_subscription
                    obj.n_trees_one_payment = nto_actual + n_trees_one_payment
                    obj.save()
                    
                except ProjectByInvestor.DoesNotExist:
                    obj = ProjectByInvestor.objects.create(
                        investor= request.user,
                        project = project
                    )
                    obj.n_trees_subscription = n_trees_subscription
                    obj.n_trees_one_payment = n_trees_one_payment
                    obj.save() 
               
            ## pagos unicos
            mis_cantidades = {}
            for item in orden.items.filter(type_inversion = 'O'):
                mis_cantidades[item.project.price_onepayment.stripe_price_id] = item.quantity 
                mis_precios = list(mis_cantidades.keys())
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
            subscription = request.user.subscription
            
            print(subscription.status)
            stripe_subscription = stripe.Subscription.modify(
                subscription.stripe_subscription_id,
                expand=['latest_invoice.payment_intent'],
                trial_end="now"
            )
            
            subscription.status=stripe_subscription.status
            print(subscription.status)
        
            subscription.save()  
            
           
            # Buscamos los items de esa suscripcion de stripe
            items_existentes = stripe.SubscriptionItem.list(
                subscription = stripe_subscription.id
            )
            mis_cantidades = {}
            mis_proyectos = {}
            for item in orden.items.filter(type_inversion = 'M'):
                mis_cantidades[item.project.price_subscription.stripe_price_id] = item.quantity
                mis_proyectos[item.project.price_subscription.stripe_price_id] =  item.project
                registrar_pbi(request.user, item.project, item.quantity, 0)
                print("registró pbi en suscripcion")
            mis_precios = list(mis_cantidades.keys())
            
            # Buscamos los items de esa suscripcion de treeconomy
            subidos_loc = []
            mis_cantidades_loc = mis_cantidades.copy()
            mis_proyectos_loc = mis_proyectos.copy()
            elements = subscription.elements.all()
            
            for element in elements:
                if element.price.stripe_price_id in mis_precios:
                    new_quantity_loc = mis_cantidades[element.price.stripe_price_id]
                    actual_quantity_loc = element.quantity
                    element.quantity = actual_quantity_loc + new_quantity_loc
                    element.save()
                    subidos_loc.append(element.price.stripe_price_id)
            
            for k in subidos_loc:
                mis_cantidades_loc.pop(k)
            print(mis_cantidades_loc)
            for item in list(mis_cantidades_loc.keys()):
                subscription_element = SubscriptionElement.objects.create(
                    subscription=subscription,
                    price= get_object_or_404(Pricing, stripe_price_id=item),
                    quantity= mis_cantidades_loc[item], 
                    project = mis_proyectos_loc[item]
                )
                subscription_element.save()
            print("llego 4")
            
            # Busca subscription Item o por el contrario la crea
            subidos= []
            print(items_existentes)
            print(mis_precios)
            for item in items_existentes:  
                if item['price']["id"] in mis_precios:
                    new_quantity = mis_cantidades[item['price']["id"]]
                    actual_quantity = item['quantity']
                    stripe.SubscriptionItem.modify(
                        item.id,
                        quantity= actual_quantity + new_quantity
                    )
                    if item['price']["id"] == settings.STRIPE_FREE_PRICE:
                        stripe.SubscriptionItem.delete(
                            item['id'],
                        )   
                    subidos.append(item['price']["id"])
            
            for k in subidos:
                mis_cantidades.pop(k)
            for item in list(mis_cantidades.keys()): 
                stripe.SubscriptionItem.create(
                    subscription=stripe_subscription.id,
                    price= item,
                    quantity= mis_cantidades[item]
                )
            
           
            datasub = {}
            datach = {}
            
            datasub.update(stripe_subscription)
            #datach.update(session)
            
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
                proration_behavior="always_invoice"
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
       
        return context

class OrderHistoryListView(generic.TemplateView):
    pass

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