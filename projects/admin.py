from django.contrib import admin

# Register your models here.
from .models import Order, OrderItem, Project, Pricing, Plat, ProjectTrackingRecord, PercentageRecord, Bill, Subscription, SubscriptionElement, Rentabilidad, Tipoarbol, Vendedor
from .forms import SubscriptionForm

class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'coordinates', 'n_trees', 'active',)
    list_filter = ('active',)
    search_fields = ('name', 'coordinates', 'tree_type',)
    #ordering = ('name',)
    
    class Meta:
        model = Project

class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'stripe_subscription_id', 'status',)
    search_fields = ('user',)
    #ordering = ('name',)
    
    class Meta:
        model = Subscription

class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'id', 'ordered')
    search_fields = ('user',)
    list_filter = ('user',)
    #ordering = ('name',)
    
    class Meta:
        model = Order

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
    list_display = ('id', 'user', 'comprador_nombre', 'comprador_id', 'city', 'vendedor')
    search_fields = ('user',)
    list_filter = ('user',)
    #ordering = ('name',)
    
    class Meta:
        model = Bill

admin.site.register(Bill, BillAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)
admin.site.register(Plat, PlatAdmin)
admin.site.register(ProjectTrackingRecord, ProjectRecordAdmin)
admin.site.register(PercentageRecord, PercentageRecordAdmin)
admin.site.register(Pricing)
admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(SubscriptionElement)
admin.site.register(Rentabilidad)
admin.site.register(Tipoarbol)
admin.site.register(Vendedor)