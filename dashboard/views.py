import re
import pandas as pd
import numpy as np
import json
from django.views.generic import TemplateView
from django.http import JsonResponse
from projects.models import Project, Order, Rentabilidad
from accounts.models import ProjectByInvestor, Company
from accounts.forms import ContactForm
from django.core import serializers
from django.template import loader
from django.http import JsonResponse
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pandas import json_normalize
from datetime import date
import calendar
from statistics import mean 
from dateutil.relativedelta import relativedelta
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
import pytz
import folium
from fastkml.kml import KML
import kml2geojson
import random
from shapely import geometry
from django.utils.translation import gettext as _
from django.shortcuts import render, redirect, reverse
from .models import CommentCompany
from .forms import CommentCompanyForm
from django.views import generic
from rolepermissions.mixins import HasRoleMixin


def generate_random(number, polygon):
    points = []
    minx, miny, maxx, maxy = polygon.bounds
    
    while len(points) < number:
        pnt = geometry.Point(random.uniform(minx, maxx), random.uniform(miny, maxy))
        
        if polygon.contains(pnt):
            points.append(geometry.Point(random.uniform(miny, maxy), random.uniform(minx, maxx),))
    return points

def popup_html(nombre, precio, hectareas, url):
    html = f"""
        <div>
                <h5 class="card-title">{nombre}</h5>
                <h6 class="card-subtitle mb-2 text-muted">{hectareas} Hectáreas</h6>
                <h4 class="card-text">{precio} USD</h4>
                <a href="{url}" style="
                background-color: #f2622e;
                border-radius: 5px;
                color: #fff;
                font-size: 18px;
                padding: 5px 15px;
                text-decoration: none;
                transition: all 0.3s; " 
                target="_blank">Invertir aquí</a>
            
        </div>
    """
    return html


def invest_json(request, usuario):
    #usuario = request.user
    pbi= ProjectByInvestor.objects.filter(investor=usuario)
    projects_id= list(map(lambda x: x.project_id, pbi))
    api = {}
    resumen = {}
    resumen_mes_anterior = {}
    inv_general = 0
    cap_general = 0
    rentabilidad= 0.0094
    
    for project_id in projects_id:
        
        fecha = Project.objects.get(pk=project_id).inicioventa_date
        hoy = datetime.today().date()
        api_fecha = {}
        total_trees = 0
        cap = 0
        cap_tot = 0
        n= 0
        
        cap_final = 0
        while fecha < hoy:
            fechafin = fecha + relativedelta(months=1)
            ordenes = Order.objects.filter(ordered_date__gte=fecha, ordered_date__lt= fechafin, user=usuario)
            fechas_ordenes = list(map(lambda x: str(x.ordered_date.date()), ordenes))
            new_trees = 0
            for orden in ordenes:
                if orden.ordered:
                    order_items = orden.items.filter(project=project_id)
                    new_trees += sum(list(map(lambda x: x.quantity, order_items )))
            total_trees += new_trees
            price = Project.objects.get(pk=project_id).price_onepayment.price
            valor_invertido = total_trees * price
            vi = "{:.2f}".format(int(valor_invertido or 0) /100)
            rent_acu = ((rentabilidad+1)**n)-1
            utilidad = rent_acu * cap
            rent = "{:.2f}".format(rentabilidad* 100)
            util_str = "{:.4f}".format(utilidad)
            cap_tot = utilidad + (valor_invertido/100)
            cap_tot__str = "{:.3f}".format(cap_tot)
            inversion = {'new_trees': new_trees, 'total_trees': total_trees, 'valor_invertido': vi, 'rentabilidad': rent, 'utilidad': util_str, 'capital': cap_tot__str}
            api_fecha[str(fecha)] = inversion
            fecha =fecha + relativedelta(months=1)
            cap = cap_tot
            n += 1
        api[Project.objects.get(pk=project_id).name] = api_fecha
        proyecto  = Project.objects.get(pk=project_id).name
        if len(api[proyecto].keys()) > 0:       
            resumen[proyecto] = api[proyecto][list(api[proyecto].keys())[-1]]   
            if len(api[proyecto].keys()) > 1:
                #si hay mes anterior
                resumen_mes_anterior[proyecto] = api[proyecto][list(api[proyecto].keys())[-2]]
            else:
                # Por si aún no hay mes anterior
                resumen_mes_anterior[proyecto] = api[proyecto][list(api[proyecto].keys())[-1]]
        
     
    return [api, resumen, resumen_mes_anterior]

def invest_api(request):
    usuario = request.user
    datos = invest_json(request, usuario)[0]
    return JsonResponse(datos)

def invest(request): 
    datos = invest_api(request)
    
    #df = json_normalize(datos)
    return render(request, 'invest.html',{
            'title': _('Tu inversión'),
            'table': "dat",
        })
    
def calculo_co2(request, usuario):
    DAYS_PER_YEAR = 365
    TREES_PER_HECTARE = 500
    CO2_CONSUMPTION_PER_HECTARE_PER_YEAR = 35000
    CO2_CONSUMPTION_PER_TREE_PER_YEAR = (CO2_CONSUMPTION_PER_HECTARE_PER_YEAR / TREES_PER_HECTARE)
    CO2_CONSUMPTION_PER_TREE_PER_DAY = (CO2_CONSUMPTION_PER_TREE_PER_YEAR / DAYS_PER_YEAR)
    pbis = ProjectByInvestor.objects.filter(investor=usuario)
    co2_total = 0
    for pbi in pbis:
        time_project = pbi.project.inicioventa_date
        hoy = date.today()
        dias = hoy - time_project
        co2_op = pbi.n_trees_subscription * dias.days * CO2_CONSUMPTION_PER_TREE_PER_DAY
        co2_su = pbi.n_trees_one_payment * dias.days * CO2_CONSUMPTION_PER_TREE_PER_DAY
        co2_total += co2_op + co2_su
    co2_consumption = "{:.2f}".format(co2_total)
    return co2_consumption    
          
def dashboard(request):
    usuario = request.user
    projects = Project.objects.all()
    invest = invest_json(request, usuario)
    datos = invest[0]
    resumen = invest[1]
    resumen_mes_anterior = invest[2]
    rentabilidad= 0.0094
    print(resumen)  
    ## Gráfca inversion
    user_projects = Project.objects.filter(name__in= list(datos.keys()))
    ## Gráfica torta y  ## Grafica árboles
    suma_inversion = 0
    suma_utilidad = 0
    suma_capital = 0
    suma_arboles_acumulados= 0
    
    suma_inversion_mes_anterior = 0
    suma_utilidad_mes_anterior = 0
    suma_capital_mes_anterior = 0
    suma_arboles_acumulados_mes_anterior= 0
    
    for key in resumen:
        suma_inversion += float(resumen[key]['valor_invertido'])
        suma_utilidad += float(resumen[key]['utilidad'])
        suma_capital += float(resumen[key]['capital'])
        #suma_arboles_nuevos += float(resumen[key]['new_trees'])
        suma_arboles_acumulados += resumen[key]['total_trees']
    
    for key in resumen_mes_anterior:
        suma_inversion_mes_anterior += float(resumen_mes_anterior[key]['valor_invertido'])
        suma_utilidad_mes_anterior += float(resumen_mes_anterior[key]['utilidad'])
        suma_capital_mes_anterior += float(resumen_mes_anterior[key]['capital'])
        #suma_arboles_nuevos += float(resumen[key]['new_trees'])
        suma_arboles_acumulados_mes_anterior += resumen_mes_anterior[key]['total_trees']
    
    suma_inversion_str = "{:,.2f}".format(suma_inversion)
    suma_utilidad_str = "{:,.2f}".format(suma_utilidad)
    suma_capital_str = "{:,.2f}".format(suma_capital)
    co2_consumption = calculo_co2(request, usuario)
    #suma_arboles_nuevos = "{:.2f}".format(suma_arboles_nuevos)
    #suma_arboles_acumulados = "{:.2f}".format(suma_arboles_acumulados) 
    resumen_general = [suma_inversion_str, suma_utilidad_str, suma_capital_str]
    
    ## Comparación con mes anterior
    if suma_utilidad_mes_anterior > 0:
        comp_utilidad = ((suma_utilidad - suma_utilidad_mes_anterior)*100)/suma_utilidad_mes_anterior
    else:
        comp_utilidad  = 0
    if suma_capital_mes_anterior > 0:
        comp_capital = "{:.2f}".format(((suma_capital - suma_capital_mes_anterior)*100)/suma_capital_mes_anterior)
    else:
        comp_capital = 0
    if suma_inversion_mes_anterior > 0:
        comp_inversion = "{:.2f}".format(((suma_inversion - suma_inversion_mes_anterior)*100)/suma_inversion_mes_anterior)
    else:
        comp_inversion = 0
    if suma_arboles_acumulados_mes_anterior:
        comp_arboles = "{:.2f}".format(((suma_arboles_acumulados - suma_arboles_acumulados_mes_anterior)*100)/suma_arboles_acumulados_mes_anterior)
    else:
        comp_arboles = 0
  
    now = datetime.now()
    dias_mes_actual = calendar.monthrange(now.year, now.month)[1]
    renta_diaria = rentabilidad / dias_mes_actual
    
    utilidad_hoy = suma_capital * renta_diaria
    utilidad_hoy_str = "{:.3f}".format(utilidad_hoy)
    
    # Rentabilidades
    my_projects = Project.objects.filter(name__in = resumen.keys())
    hoy = datetime.today()
    year = hoy.strftime("%Y")
    month = hoy.strftime("%m")
    
    rentabilidades = Rentabilidad.objects.filter(project__in=my_projects).filter(year=year).filter(month=month)
    try:
        renta_promedio = round(mean(rentabilidades.values_list('valor', flat=True)), 3)
    except:
        renta_promedio = 1.95

    # Carbono en kilogramos
    hombre= 2000
    carro = 2145
    camion = 2560
    avion = 3300
    

    # CO2 por arbol en un año en kilogramos 
    arbol_anio_co2 = 33

    anios_arboles = []
    co2_desdecompra = 0
    # Calculo de co2
    ordenes = Order.objects.filter(user=usuario)
    for order in ordenes:
        #anios = order.ordered_date.year - datetime.today().year
        diff = (relativedelta(datetime.today().replace(tzinfo=pytz.utc), order.ordered_date).months)/12
        for item in order.items.all():
            co2_desdecompra += arbol_anio_co2 * diff * item.quantity
            
    progreso_co2 = str(round((float(co2_consumption) *100)/avion, 3))
  
    return render(request, 'argon.html',{
        'title': _('Tablero'),
        'mensaje': _("Hola, como estas?"),
        'projects': projects,
        'user_projects': user_projects,
        'datos': datos,
        'resumen_general': resumen_general,
        'resumen_dict': resumen,
        'inversion_total': resumen_general[0],
        'utilidad_total': resumen_general[1],
        'capital_total': resumen_general[2],
        'arboles_total': suma_arboles_acumulados,
        'rentabilidad': renta_promedio,
        'rentabilidades': rentabilidades,
        'co2_consumption': co2_consumption, 
        'co2_desdecompra': co2_desdecompra,
        'progreso_co2': progreso_co2,
        'comp_utilidad': comp_utilidad, 
        'comp_capital': comp_capital, 
        'comp_inversion': comp_inversion, 
        'comp_arboles': comp_arboles,
        'utilidad_hoy': utilidad_hoy_str,
        
    })   

def dashboard_company(request, slug):
    company = Company.objects.get(pk=slug)
    usuario = company.user
    company_name = company.name

    if company.logotipo:
        tiene_logo = True
    else:
        tiene_logo = False

    if company.portadas:
        tiene_fondo = True
    else:
        tiene_fondo = False
    
    projects = Project.objects.all()
    invest = invest_json(request, usuario)
    datos = invest[0]
    resumen = invest[1]
    resumen_mes_anterior = invest[2]
    rentabilidad= 0.0094
    
    ## Gráfca inversion
    user_projects = Project.objects.filter(name__in= list(datos.keys()))
    ## Gráfica torta y  ## Grafica árboles
    suma_inversion = 0
    suma_utilidad = 0
    suma_capital = 0
    suma_arboles_acumulados= 0
    
    suma_inversion_mes_anterior = 0
    suma_utilidad_mes_anterior = 0
    suma_capital_mes_anterior = 0
    suma_arboles_acumulados_mes_anterior= 0
    
    for key in resumen:
        suma_inversion += float(resumen[key]['valor_invertido'])
        suma_utilidad += float(resumen[key]['utilidad'])
        suma_capital += float(resumen[key]['capital'])
        #suma_arboles_nuevos += float(resumen[key]['new_trees'])
        suma_arboles_acumulados += resumen[key]['total_trees']
    
    for key in resumen_mes_anterior:
        suma_inversion_mes_anterior += float(resumen_mes_anterior[key]['valor_invertido'])
        suma_utilidad_mes_anterior += float(resumen_mes_anterior[key]['utilidad'])
        suma_capital_mes_anterior += float(resumen_mes_anterior[key]['capital'])
        #suma_arboles_nuevos += float(resumen[key]['new_trees'])
        suma_arboles_acumulados_mes_anterior += resumen_mes_anterior[key]['total_trees']
    
    suma_inversion_str = "{:,.2f}".format(suma_inversion)
    suma_utilidad_str = "{:,.2f}".format(suma_utilidad)
    suma_capital_str = "{:,.2f}".format(suma_capital)
    co2_consumption = calculo_co2(request, usuario)
    #suma_arboles_nuevos = "{:.2f}".format(suma_arboles_nuevos)
    #suma_arboles_acumulados = "{:.2f}".format(suma_arboles_acumulados) 
    resumen_general = [suma_inversion_str, suma_utilidad_str, suma_capital_str]
    
    ## Comparación con mes anterior
    if suma_utilidad_mes_anterior > 0:
        comp_utilidad = ((suma_utilidad - suma_utilidad_mes_anterior)*100)/suma_utilidad_mes_anterior
    else:
        comp_utilidad  = 0
    if suma_capital_mes_anterior > 0:
        comp_capital = "{:.2f}".format(((suma_capital - suma_capital_mes_anterior)*100)/suma_capital_mes_anterior)
    else:
        comp_capital = 0
    if suma_inversion_mes_anterior > 0:
        comp_inversion = "{:.2f}".format(((suma_inversion - suma_inversion_mes_anterior)*100)/suma_inversion_mes_anterior)
    else:
        comp_inversion = 0
    if suma_arboles_acumulados_mes_anterior:
        comp_arboles = "{:.2f}".format(((suma_arboles_acumulados - suma_arboles_acumulados_mes_anterior)*100)/suma_arboles_acumulados_mes_anterior)
    else:
        comp_arboles = 0
  
    now = datetime.now()
    dias_mes_actual = calendar.monthrange(now.year, now.month)[1]
    renta_diaria = rentabilidad / dias_mes_actual
    
    utilidad_hoy = suma_capital * renta_diaria
    utilidad_hoy_str = "{:.3f}".format(utilidad_hoy)
    
    # Rentabilidades
    my_projects = Project.objects.filter(name__in = resumen.keys())
    hoy = datetime.today()
    year = hoy.strftime("%Y")
    month = hoy.strftime("%m")
    
    rentabilidades = Rentabilidad.objects.filter(project__in=my_projects).filter(year=year).filter(month=month)
    try:
        renta_promedio = round(mean(rentabilidades.values_list('valor', flat=True)), 3)
    except:
        renta_promedio = 1.95

    # Carbono en kilogramos
    hombre= 2000
    carro = 2145
    camion = 2560
    avion = 3300
    

    # CO2 por arbol en un año en kilogramos 
    arbol_anio_co2 = 33

    anios_arboles = []
    co2_desdecompra = 0
    # Calculo de co2
    ordenes = Order.objects.filter(user=usuario)
    for order in ordenes:
        #anios = order.ordered_date.year - datetime.today().year
        diff = (relativedelta(datetime.today().replace(tzinfo=pytz.utc), order.ordered_date).months)/12
        for item in order.items.all():
            co2_desdecompra += arbol_anio_co2 * diff * item.quantity
            
    progreso_co2 = str(round((float(co2_consumption) *100)/avion, 3))

    ## Mapa 
    initialMap = folium.Map(location=[4.6486259,-74.2478921], zoom_start=6, tiles=None)
    projects = Project.objects.all()
    for project in projects:
        if project.geokml:
            lotes = kml2geojson.main.convert(project.geokml)
            geometria = lotes[0]["features"][0]["geometry"]
            poligono = geometry.Polygon(geometria["coordinates"][0])
            punto_shapely = generate_random(1, poligono)
            html = popup_html(project.name, project.get_price(), project.n_hectares, project.get_absolute_url())
            popup = folium.Popup(folium.Html(html, script=True), max_width=500)
            punto = list(punto_shapely[0].coords)[0]
            folium.Marker(punto, popup=popup,   icon=folium.Icon(color='lightgreen', icon_color='darkgreen', icon='tree', prefix='fa')).add_to(initialMap)
            folium.GeoJson(data=geometria).add_to(initialMap)
    mapbox_token = settings.MAPBOX_TOKEN
    tile = folium.TileLayer(
        tiles= f'https://api.mapbox.com/styles/v1/alejocruzrcc/clf96goiq000401mnwfmleh76/tiles/256/{{z}}/{{x}}/{{y}}@2x?access_token={mapbox_token}',
        attr = 'Mapbox Satelite',
        name = 'Satélite',
        overlay = False,
        control = True
    ).add_to(initialMap)
    """
    tile = folium.TileLayer(
        tiles = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr = 'Esri',
        name = 'Satélite',
        overlay = False,
        control = True
    ).add_to(initialMap)

    folium.TileLayer('openstreetmap').add_to(initialMap)
    folium.LayerControl().add_to(initialMap)       
    """   
    ###

    ## Vehículos
    vehiculos = {}
    
    
    vehiculos["transporte-publico"] = { 
                          "id": "transporte-publico",
                          "nombre": _("Transporte Público"),                  
                          "url": 'dashboard/img/company/img/icono_bus.png',
                          "icono": "<i class='fas fa-bus fa-2x'></i>",
                          "mensaje": _('Un autobús de transporte público promedio que funciona con diesel emite alrededor de 104.6 toneladas métricas de CO2 por año. Esta cifra se basa en la suposición de que el autobús recorre una distancia promedio de 50,000 millas (aproximadamente 80,500 kilómetros) por año, y su eficiencia de combustible es de 4.6 millas por galón (aproximadamente 2 kilómetros por litro).'),
                          }
    
    vehiculos["automovil"] = { 
                          "id": "automovil",
                          "nombre": _("Automóvil"),
                          "url": 'dashboard/img/company/img/auto.png',
                          "icono": "<i class='fas fa-car fa-2x'></i>",
                          "mensaje": _("La cantidad de dióxido de carbono (CO2) emitido por un automóvil promedio al año depende de varios factores, como el modelo del automóvil, la eficiencia de su motor, la distancia recorrida y las condiciones de conducción. Sin embargo, se puede proporcionar una estimación aproximada de la cantidad de CO2 que emite un automóvil promedio al año equivalente a 2145 Kg"),
                          }
    vehiculos["moto"] = { 
                          "id": "moto",  
                          "nombre": _("Moto"),
                          "url": 'dashboard/img/company/img/icono_moto.png',
                          "icono": "<i class='fas fa-motorcycle fa-2x'></i>",
                          "mensaje": _("Una motocicleta promedio emite alrededor de 4.6 toneladas métricas de CO2 por año. Esta cifra se basa en la suposición de que la motocicleta recorre una distancia promedio de 4,000 millas (aproximadamente 6,400 kilómetros) por año y su eficiencia de combustible es de 50 millas por galón (aproximadamente 21 kilómetros por litro)."),
                          }
    
    vehiculos["avion"] = { 
                          "id": "avion",
                          "nombre": _("Avión"),
                          "url": 'dashboard/img/company/img/icono_avion.png',
                          "icono": "<i class='fas fa-plane fa-2x'></i>",
                          "mensaje": _("Un vuelo promedio de un avión comercial de pasajeros de larga distancia que recorre una distancia de 7,500 millas (aproximadamente 12,070 kilómetros) emite alrededor de 3,933 kilogramos de CO2. Si asumimos que un avión comercial promedio realiza alrededor de 3 vuelos al día y 300 días al año, entonces la cantidad de CO2 que emite en un año sería de alrededor de 3.54 millones de kilogramos (o 3,540 toneladas métricas) de CO2."),
                          }
    
    ## Rangos de Carbono por vehículo al año:

    # Carro: 2145 kg
    # Avión: 3900 Kg
    # Moto: 4600 Kg
    # Bus transportte público: 104.600

    vehiculo_nombre = ""

    # Switch case para asignar vehículo según el valor de co2_desdecompra
    if co2_desdecompra <= 2145:
        vehiculo_nombre = "automovil"
    elif co2_desdecompra <= 3900:
        vehiculo_nombre = "avion"
    elif co2_desdecompra <= 4600:
        vehiculo_nombre = "moto"
    else:
        vehiculo_nombre = "transporte-publico"

    vehiculo = vehiculos[vehiculo_nombre]

    print(vehiculo["url"])

    ###
    ### Contactanos
    form_contactanos = ContactForm(request.POST or None, request.FILES or None)
    if request.method == 'POST':
        if form_contactanos.is_valid():
            messages.info(request, "Hemos recibido tu mensaje")
            name = form_contactanos.cleaned_data.get('name')
            email = form_contactanos.cleaned_data.get('email')
            message = form_contactanos.cleaned_data.get('message')
            phone = form_contactanos.cleaned_data.get('phone')
            
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
    ###
    print(user_projects)

    ## Comentarios
    comments = company.comments.filter(approved_comment=True)
    form = CommentCompanyForm()
    if request.method == 'POST':
        form = CommentCompanyForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.company = company
            comment.approved_comment = True
            comment.save()
            return redirect('dashboard_company', slug=company.slug)

    else:
        form = CommentCompanyForm()
        
    return render(request, 'company.html', {
        'projects': projects,
        'user_projects': user_projects,
        'datos': datos,
        'resumen_general': resumen_general,
        'resumen_dict': resumen,
        'inversion_total': resumen_general[0],
        'utilidad_total': resumen_general[1],
        'capital_total': resumen_general[2],
        'arboles_total': suma_arboles_acumulados,
        'rentabilidad': renta_promedio,
        'rentabilidades': rentabilidades,
        'co2_consumption': co2_consumption, 
        'co2_desdecompra': co2_desdecompra,
        'progreso_co2': progreso_co2,
        'comp_utilidad': comp_utilidad, 
        'comp_capital': comp_capital, 
        'comp_inversion': comp_inversion, 
        'comp_arboles': comp_arboles,
        'utilidad_hoy': utilidad_hoy_str,
        'company_name': company_name,
        'company': company,
        'tiene_logo': tiene_logo,
        'tiene_fondo': tiene_fondo, 
        "map": initialMap._repr_html_(),
        "vehiculo": vehiculo,
        "vehiculo_nombre": vehiculo_nombre,
        "form_contactanos": form_contactanos,
        "comments": comments,
        "form": form
    })
    
class CompanyListView(HasRoleMixin, generic.TemplateView):
    allowed_roles = 'admin'
    model = Company
    template_name = 'companies.html'

    
    def get_context_data(self, *args, **kwargs):
        context = super(CompanyListView, self).get_context_data(*args, **kwargs) 
        context['companies'] = Company.objects.all().order_by('-created_at')     
        return context