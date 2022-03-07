from django.shortcuts import render
from django.views import generic

from .models import Project

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
    
    

    
