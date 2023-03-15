from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.views import generic
from .forms import ProjectForm, AddToCartForm, BillForm
from .models import Project, OrderItem, Bill
from rolepermissions.decorators import has_role_decorator
from billing.utils import get_or_set_order_session
from accounts import views 
from accounts.models import User, Video
from django.contrib import messages
import folium
from folium.plugins import MarkerCluster
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from fastkml.kml import KML
import kml2geojson
import random
from shapely import geometry
import os

# Create your views here.
class ProjectListView(generic.ListView):
    model = Project
    template_name = 'project_list.html'

    def get_queryset(self):
        return Project.objects.get_queryset()

    def get_context_data(self, *args, **kwargs):
        context = super(ProjectListView, self).get_context_data(*args, **kwargs)
        context["video_que_es"] = get_object_or_404(Video, nombre= "que_es_treeconomy")
        context["video_impacto"] = get_object_or_404(Video, nombre= "impacto")
        context["name"] = 'Proyectos'
        return context

class MapaView(generic.TemplateView):
    template_name = 'projects_map.html'
    
    def get_context_data(self, *args, **kwargs):
        fig = folium.Figure(height="750vh")
        initialMap = folium.Map(location=[4.6486259,-74.2478921], zoom_start=6).add_to(fig)
        projects = Project.objects.all()
        mCluster = MarkerCluster(name="proyectos").add_to(initialMap)
        for project in projects:
            if project.geokml:
                lotes = kml2geojson.main.convert(project.geokml)
                geometria = lotes[0]["features"][0]["geometry"]
                poligono = geometry.Polygon(geometria["coordinates"][0])
                punto_shapely = generate_random(1, poligono)
                html = popup_html(project.name, project.resena, project.n_hectares, project.get_absolute_url())
                popup = folium.Popup(folium.Html(html, script=True), max_width=500)
                punto = list(punto_shapely[0].coords)[0]
                folium.Marker(punto, popup=popup,  icon=folium.Icon(color='lightgreen', icon_color='darkgreen', icon='tree', prefix='fa')).add_to(mCluster)
                folium.GeoJson(data=geometria).add_to(initialMap)
        
        
        mapbox_token = settings.MAPBOX_TOKEN
        tile = folium.TileLayer(
            tiles= f'https://api.mapbox.com/styles/v1/alejocruzrcc/clf96goiq000401mnwfmleh76/tiles/256/{{z}}/{{x}}/{{y}}@2x?access_token={mapbox_token}',
            attr = 'Mapbox Satelite',
            name = 'Satélite',
            overlay = False,
            control = True
        ).add_to(initialMap)
        
        #folium.TileLayer('openstreetmap').add_to(initialMap)
        #folium.LayerControl().add_to(initialMap)       
        context = {
            "map": initialMap._repr_html_(),
            "projects":  projects}
        return context

class ProjectDetailListView(LoginRequiredMixin, generic.FormView):
    model = Project
    template_name = 'project_detail.html'
    form_class = AddToCartForm
    
    def get_queryset(self):
        return Project.objects.get_queryset()
    
    def get_context_data(self, *args, **kwargs):
        f = folium.Figure(height=500)
        context = super(ProjectDetailListView, self).get_context_data(*args, **kwargs)
        if self.get_object().geokml != None:
            lotes = kml2geojson.main.convert(self.get_object().geokml)
            geometria = lotes[0]["features"][0]["geometry"]
            poligono = geometry.Polygon(geometria["coordinates"][0])
            punto_shapely = generate_random(1, poligono)
            punto = list(punto_shapely[0].coords)[0]
        else:
            punto = [4.6486259,-74.2478921]

        detailMap= folium.Map(location=punto, zoom_start=14, tiles=None).add_to(f)
        folium.GeoJson(data=geometria, name="Polígono").add_to(detailMap)
        
        mapbox_token = settings.MAPBOX_TOKEN
        tile = folium.TileLayer(
            tiles= f'https://api.mapbox.com/styles/v1/alejocruzrcc/clf96goiq000401mnwfmleh76/tiles/256/{{z}}/{{x}}/{{y}}@2x?access_token={mapbox_token}',
            attr = 'Mapbox Satelite',
            name = 'Satélite',
            overlay = False,
            control = True
        ).add_to(detailMap)
        """
        tile = folium.TileLayer(
            tiles = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
            attr = 'Esri',
            name = 'Satélite',
            overlay = False,
            control = True
        ).add_to(detailMap)
        """
        #folium.TileLayer('openstreetmap').add_to(detailMap)
        #folium.LayerControl().add_to(detailMap)
        
        context["project"] = self.get_object()
        context["activo"] = self.get_object().active
        context["order"] = get_or_set_order_session(self.request)
        context["map_detail"] = detailMap._repr_html_()
        return context
    
    def get_object(self):
        return get_object_or_404(Project, slug = self.kwargs["slug"])
    
    def get_success_url(self):
        return reverse("summary")
    
    def get_form_kwargs(self):
        kwargs = super(ProjectDetailListView, self).get_form_kwargs()
        kwargs["project_id"] = self.get_object().name
        return kwargs
    
    def form_valid(self, form):
        order = get_or_set_order_session(self.request)
        
        project = self.get_object()
        type_inversion = form.cleaned_data['type_inversion']
        item_filter = order.items.filter(project = project, type_inversion= type_inversion)
        if item_filter.exists():
            item = item_filter.first()
            item.quantity += int(form.cleaned_data['quantity'])
            item.save()
        else: 
            new_item = form.save(commit=False)
            new_item.project = project
            new_item.order = order
            new_item.save()
        return super(ProjectDetailListView, self).form_valid(form)

class CartView(generic.TemplateView):
    template_name = 'cart.html'
    
    def get_context_data(self, *args, **kwargs):
        context = super(CartView, self).get_context_data(**kwargs)
        context["order"] = get_or_set_order_session(self.request)
        return context
   
class IncreaseQuantityCartView(generic.View):
    def get(self, request, *args, **kwargs):    
        order_item = get_object_or_404(OrderItem, id=kwargs['pk'])
        order_item.quantity += 1
        order_item.save()
        return redirect("summary")

class DecreaseQuantityCartView(generic.View):
    def get(self, request, *args, **kwargs):
        order_item = get_object_or_404(OrderItem, id=kwargs['pk'])
        if order_item.quantity <= 1:
            order_item.delete()
        else: 
            order_item.quantity -= 1
            order_item.save()
        return redirect("summary")
    
class RemoveFromCartView(generic.View):
    def get(self, request, *args, **kwargs):
        order_item = get_object_or_404(OrderItem, id=kwargs['pk'])
        order_item.delete()
        return redirect("summary")
 
class FacturacionView(generic.FormView): 
    template_name= 'facturacion.html' 
    form_class = BillForm  

    def get_success_url(self):
        return reverse("billing:checkout")

    def form_valid(self, form):
        order = get_or_set_order_session(self.request)
        #selected_billing_address =form.cleaned_data.get('selected_billing_address')
        selected_billing_address = False
        if selected_billing_address:
            print("hay factura")
            order.bill = selected_billing_address
        else:
            bill = Bill.objects.create(
                address_type = 'B',
                user =self.request.user,
                comprador_nombre=form.cleaned_data['comprador_nombre'],
                comprador_id=form.cleaned_data['comprador_id'],
                comprador_email= form.cleaned_data['comprador_email'],
                comprador_phone= form.cleaned_data['comprador_phone'],
                beneficiario_nombre=form.cleaned_data['beneficiario_nombre'],
                beneficiario_id=form.cleaned_data['beneficiario_id'],
                beneficiario_email= form.cleaned_data['beneficiario_email'],
                beneficiario_phone= form.cleaned_data['beneficiario_phone'],
                address_line_1=form.cleaned_data['billing_address_line_1'],
                address_line_2=form.cleaned_data['billing_address_line_2'],
                zip_code=form.cleaned_data['billing_zip_code'],
                city=form.cleaned_data['billing_city'],
                vendedor= form.cleaned_data['vendedor']
            )
            bill.save()
            order.bill = bill
            
        order.save()
        messages.info(self.request, "Agregaste exitosamente tu información de facturación")
        return super(FacturacionView, self).form_valid(form)
    
    def form_invalid(self, form):
        print(form.errors)
        messages.warning(self.request, form.errors)
        return super(FacturacionView, self).form_invalid(form)
    
    def get_form_kwargs(self):
        kwargs = super(FacturacionView, self).get_form_kwargs()
        kwargs['user_id'] = self.request.user.id
        return kwargs
    
    def get_context_data(self, *args, **kwargs):
        context = super(FacturacionView, self).get_context_data(**kwargs)
        context["order"] = get_or_set_order_session(self.request)
        user_bills = Bill.objects.filter(user=self.request.user.id)
        if not user_bills:
            form = BillForm(user_id=self.request.user.id)
        else:
            last_bill = user_bills.latest('id')
            dict = {
                'id': last_bill.id,
                'user_id': last_bill.user.id, 
                'comprador_nombre': last_bill.comprador_nombre, 
                'comprador_id': last_bill.comprador_id, 
                'comprador_email': last_bill.comprador_email, 
                'comprador_phone':   last_bill.comprador_phone,
                'beneficiario_nombre': last_bill.beneficiario_nombre, 
                'beneficiario_id': last_bill.beneficiario_id, 
                'beneficiario_email': last_bill.beneficiario_email, 
                'beneficiario_phone': last_bill.beneficiario_phone,
                'billing_address_line_1': last_bill.address_line_1, 
                'billing_address_line_2': last_bill.address_line_2, 
                'billing_address_type': last_bill.address_type, 
                'billing_city': last_bill.city, 
                'billing_zip_code': last_bill.zip_code
            }
            form = BillForm(user_id=self.request.user.id, initial = dict)
        context["form"] = form
        return context
   
@has_role_decorator('admin')   
def crear(request):
    #import pdb; pdb.set_trace()
    formulario = ProjectForm(request.POST or None, request.FILES or None)
    if formulario.is_valid():
        formulario.save()
        return redirect('/projects')
    return render(request, "create.html", {'formulario': formulario})

@has_role_decorator('admin')  
def eliminar(request, pk):
  project = Project.objects.get(pk=pk)
  #import pdb; pdb.set_trace() 
  project.delete()
  return redirect('projects')

@has_role_decorator('admin')  
def editar(request, pk):
    project = Project.objects.get(pk=pk)
    formulario = ProjectForm(request.POST or None, request.FILES or None, instance=project)
     
    if formulario.is_valid() and request.POST:
        formulario.save()
        return redirect('projects')
    else:
        errores = formulario.errors

    return render(request, "edit.html", {'formulario': formulario, 'errores': errores})
    
def generate_random(number, polygon):
    points = []
    minx, miny, maxx, maxy = polygon.bounds
    
    while len(points) < number:
        pnt = geometry.Point(random.uniform(minx, maxx), random.uniform(miny, maxy))
        
        if polygon.contains(pnt):
            points.append(geometry.Point(random.uniform(miny, maxy), random.uniform(minx, maxx),))
    return points

def read_kml(fname='ss.kml'):
    kml = KML()
    kml.from_string(open(fname).read().encode())
    points = dict()
    
    for feature in kml.features():
        for placemark in feature.features():
            if placemark.styleUrl.startswith('#AREA'):
                points.update({placemark.name:
                            (placemark.geometry.y, placemark.geometry.x, )})
    
    return points
    
def popup_html(nombre, descripcion, hectareas, url):
    html = f"""
    <div class="card">
        <div class="card-body">
            <h3 class="card-title">Proyecto {nombre}</h3>
            <h6 class="card-subtitle mb-2 text-muted">{hectareas} Hectáreas</h6>
            <p class="card-text">{descripcion}</p>
            <h4><a href="{ url }" class="card-link" target="_blank">Invertir aquí</a></h4>
        </div>
    </div>
    """
    return html

    
