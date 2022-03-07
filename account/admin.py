from django.contrib import admin
from django.contrib.auth.models import Permission
from .models import Profile
from .forms import SubscriptionForm
from .models import Subscription, ProjectByInvestor

class SubscriptionAdmin(admin.ModelAdmin):
    form = SubscriptionForm
    search_fields = ['status', 'investor']
    
    class Meta:
        model = Subscription

class ProjectInvestorAdmin(admin.ModelAdmin):
    search_fields = ['active', 'project', 'investor']

    class Meta:
        model = ProjectByInvestor

admin.site.register(Profile)
admin.site.register(Permission)
admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(ProjectByInvestor, ProjectInvestorAdmin)
