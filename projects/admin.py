from django.contrib import admin

# Register your models here.
from .models import Order, OrderItem, Project, Pricing, Plat, ProjectTrackingRecord, PercentageRecord, Bill, Subscription
from .forms import SubscriptionForm

class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'coordinates', 'n_trees', 'tree_type', 'active',)
    list_filter = ('active',)
    search_fields = ('name', 'coordinates', 'tree_type',)
    #ordering = ('name',)
    
    class Meta:
        model = Project

class PlatAdmin(admin.ModelAdmin):
    list_display = ('plat_id', 'project', 'n_trees',)
    search_fields = ('plat_id', 'project', 'n_trees',)
    
    class Meta:
        model = Plat

class ProjectRecordAdmin(admin.ModelAdmin):
    list_display = ('heigth', 'dch', 'volume', 'age', 'record_date')
    search_fields = ['plat', 'profitability', 'heigth', 'age']
    
    class Meta:
        model = ProjectTrackingRecord

class PercentageRecordAdmin(admin.ModelAdmin):
    list_display = ('project', 'record_date', 'growth_avg', 'dch_avg', 'growth_pctg', 'dch_pctg')
    search_fields = ('project', 'record_date')

    class Meta:
        model = PercentageRecord
        
class BillAdmin(admin.ModelAdmin):
    list_display = [
        'address_line_1',
        'address_line_2',
        'zip_code',
        'city',
        'address_type',
    ]
    

admin.site.register(Bill)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Plat, PlatAdmin)
admin.site.register(ProjectTrackingRecord, ProjectRecordAdmin)
admin.site.register(PercentageRecord, PercentageRecordAdmin)
admin.site.register(Pricing)
admin.site.register(Subscription)