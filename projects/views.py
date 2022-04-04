from django.shortcuts import render, redirect
from django.views import generic
from .forms import ProjectForm
from .models import Project
from rolepermissions.decorators import has_role_decorator

# Create your views here.
class ProjectListView(generic.ListView):
    model = Project
    template_name = 'project_list.html'

    def get_queryset(self):
        return Project.objects.get_queryset()

    def get_context_data(self, *args, **kwargs):
        context = super(ProjectListView, self).get_context_data(*args, **kwargs)
        context["title"] = 'List of all active projects'
        return context

class ProjectDetailListView(generic.DetailView):
    model = Project
    template_name = 'project_detail.html'

    def get_queryset(self):
        return Project.objects.get_queryset()
    
    def get_context_data(self, *args, **kwargs):
        context = super(ProjectDetailListView, self).get_context_data(*args, **kwargs)
        context["title"] = 'Detail of each project'
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
    

    
