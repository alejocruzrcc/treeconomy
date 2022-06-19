from django.contrib import admin
from django.contrib.auth.models import Permission

from .models import Profile, User

from .models import ProjectByInvestor


class ProjectInvestorAdmin(admin.ModelAdmin):
    search_fields = ['active', 'project', 'investor']

    class Meta:
        model = ProjectByInvestor

admin.site.register(Profile)
admin.site.register(Permission)
admin.site.register(ProjectByInvestor, ProjectInvestorAdmin)
