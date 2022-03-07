from django.contrib import admin
from .models import BillingProfile

# Register your models here.
#class BillingProfileAdmin(admin.ModelAdmin):
admin.site.register(BillingProfile)