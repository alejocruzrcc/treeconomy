from django.contrib import admin
from django.contrib.auth.models import Permission

from .models import Profile, User

from .models import ProjectByInvestor
from .models import Video


class ProjectByInvestorAdmin(admin.ModelAdmin):
    list_display = ('id', 'investor', 'project', 'n_trees_subscription', 'n_trees_one_payment',)
   
    list_filter = ('project',)
    #ordering = ('name',)
    
    class Meta:
        model = ProjectByInvestor



class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'tipocliente',)
   
    list_filter = ('tipocliente',)
    #ordering = ('name',)
    
    class Meta:
        model = Profile

admin.site.register(Video)

admin.site.register(Profile, ProfileAdmin)
admin.site.register(Permission)
admin.site.register(ProjectByInvestor, ProjectByInvestorAdmin)
