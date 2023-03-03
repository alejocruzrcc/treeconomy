import re
import pandas as pd
import numpy as np
import json
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.shortcuts import render
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



def generate_random(number, polygon):
    points = []
    minx, miny, maxx, maxy = polygon.bounds
    
    while len(points) < number:
        pnt = geometry.Point(random.uniform(minx, maxx), random.uniform(miny, maxy))
        
        if polygon.contains(pnt):
            points.append(geometry.Point(random.uniform(miny, maxy), random.uniform(minx, maxx),))
    return points

def popup_html(nombre, descripcion, hectareas, url):
    html = f"""
    <div class="card" style="width: 40rem;">
        <div class="card-body">
            <h3 class="card-title">Proyecto {nombre}</h3>
            <h6 class="card-subtitle mb-2 text-muted">{hectareas} Hectáreas</h6>
            <p class="card-text">{descripcion}</p>
            <h4><a href="{ url }" class="card-link" target="_blank">Invertir aquí</a></h4>
        </div>
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
    
    suma_inversion_str = "{:.2f}".format(suma_inversion)
    suma_utilidad_str = "{:.2f}".format(suma_utilidad)
    suma_capital_str = "{:.2f}".format(suma_capital)
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
            
    progreso_co2 = round((float(co2_consumption) *100)/avion, 3)
    return render(request, 'argon.html',{
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

    if company.logotipo != None:
        tiene_logo = True
    else:
        tiene_logo = False
    if company.portadas != None:
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
    
    suma_inversion_str = "{:.2f}".format(suma_inversion)
    suma_utilidad_str = "{:.2f}".format(suma_utilidad)
    suma_capital_str = "{:.2f}".format(suma_capital)
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
            
    progreso_co2 = round((float(co2_consumption) *100)/avion, 3)

    ## Mapa 
    initialMap = folium.Map(location=[4.6486259,-74.2478921], zoom_start=6, tiles=None)
    projects = Project.objects.all()
    for project in projects:
        if project.geokml != None:
            lotes = kml2geojson.main.convert(project.geokml)
            geometria = lotes[0]["features"][0]["geometry"]
            poligono = geometry.Polygon(geometria["coordinates"][0])
            punto_shapely = generate_random(1, poligono)
            html = popup_html(project.name, project.resena, project.n_hectares, project.get_absolute_url())
            popup = folium.Popup(folium.Html(html, script=True), max_width=500)
            punto = list(punto_shapely[0].coords)[0]
            folium.Marker(punto, popup=popup).add_to(initialMap)
            folium.GeoJson(data=geometria).add_to(initialMap)
    tile = folium.TileLayer(
        tiles = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr = 'Esri',
        name = 'Satélite',
        overlay = False,
        control = True
    ).add_to(initialMap)
    folium.TileLayer('openstreetmap').add_to(initialMap)
    folium.LayerControl().add_to(initialMap)       
        
    ###

    ## Vehículos
    vehiculos = {}
    
    vehiculos["moto"] = { "nombre": "Moto",
                          "url": 'dashboard/img/company/img/icono_moto.png',
                          }
    vehiculos["automovil"] = { "nombre": "Automovil",
                          "url": 'dashboard/img/company/img/icono_automovil.png',
                          }
    vehiculos["bus"] = { "nombre": "Bus",
                          "url": 'dashboard/img/company/img/icono_bus.png',
                          }
    vehiculos["avion"] = { "nombre": "Avión",
                          "url": 'dashboard/img/company/img/icono_avion.png',
                          }
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
        "vehiculos": vehiculos,
        "form_contactanos": form_contactanos,
    })
    
