from __future__ import division
from ast import arg
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils.text import slugify
from django.core.validators import MinValueValidator
from django.db.models.signals import pre_save
from datetime import datetime, timedelta
#from django.utils import timezone
from django.contrib.auth.models import User
from django.conf import settings
from statistics import mean
import math
import stripe

stripe.api_key = settings.STRIPE_PRIVATE_KEY
DAYS_PER_YEAR = 365
TREES_PER_HECTARE = 500
CO2_CONSUMPTION_PER_HECTARE_PER_YEAR = 35000
CO2_CONSUMPTION_PER_TREE_PER_YEAR = (CO2_CONSUMPTION_PER_HECTARE_PER_YEAR / TREES_PER_HECTARE)
CO2_CONSUMPTION_PER_TREE_PER_DAY = (CO2_CONSUMPTION_PER_TREE_PER_YEAR / DAYS_PER_YEAR)

class Bill(models.Model):
    ADDRESS_CHOICES= (
        ('B', 'Billing'),
        ('S', 'Shipping'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address_line_1 = models.CharField(max_length=150)
    address_line_2 = models.CharField(max_length=150)
    address_type = models.CharField(max_length=1, choices=ADDRESS_CHOICES)
    default = models.BooleanField(default=False)
    
    city = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=100)
        
    def __str(self):
        return f"{self.address_line_1}, {self.address_line_2}, {self.city}, {self.zip_code}"
    
    class Meta:
        verbose_name_plural= "Bills"

class Bill2(models.Model):
    ADDRESS_CHOICES= (
        ('B', 'Billing'),
        ('S', 'Shipping'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address_line_1 = models.CharField(max_length=150)
    address_line_2 = models.CharField(max_length=150)
    address_type = models.CharField(max_length=1, choices=ADDRESS_CHOICES)
    default = models.BooleanField(default=False)
    
    city = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=100)
        
    def __str(self):
        return f"{self.address_line_1}, {self.address_line_2}, {self.city}, {self.zip_code}"
    
    class Meta:
        verbose_name_plural= "Bills2"
class ProjectQuerySet(models.query.QuerySet):
    def active(self):
        return self.filter(active=True)

    def search(self, query):
        lookups = (Q(coordinates__icontains=query) | 
                   Q(name__icontains=query) 
                  )      
class ProjectManager(models.Manager):
    def get_queryset(self):
        return ProjectQuerySet(self.model, using=self._db)
    
    def all(self):
        return self.get_queryset().active()
    
    def get_by_id(self, id):
        qs = self.get_queryset().filter(pk=id) # Product.objects == self.get_queryset()
        if qs.count() == 1:
            return qs.first()
        return None
    
    def search(self, query):
        return self.get_queryset().active().search(query)

class Pricing(models.Model):
    name= models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    stripe_price_id = models.CharField(max_length=50)
    price = models.IntegerField(default=0)
    currency = models.CharField(max_length=50)

    def __str__(self):
        return self.name
    
class Subscription(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    pricing = models.ForeignKey(Pricing, on_delete=models.CASCADE, related_name='subscriptions')
    created = models.DateTimeField(auto_now_add=True)
    stripe_subscription_id = models.CharField(max_length=50)
    status = models.CharField(max_length=100)
    n_projects      = models.PositiveIntegerField()

    class Meta:
        verbose_name = "Subscription"
        verbose_name_plural = "Subscriptions"
        ordering = ['-created']

    def __str__(self):
        return self.user.email

    @property
    def is_active(self):
        return self.status == "active" or self.status == "closed"

class Project(models.Model):
    name                = models.CharField(max_length=120)
    slug                = models.SlugField(unique=True, primary_key=True) 
    coordinates         = models.CharField(max_length=120)
    n_trees             = models.PositiveIntegerField()
    plantation_date     = models.DateField()
    price_onepayment    = models.ForeignKey(Pricing, related_name='projects_onepayment', blank=True, null=True, on_delete=models.SET_NULL)
    price_subscription   = models.ForeignKey(Pricing, related_name='projects_subscription', blank=True, null=True, on_delete=models.SET_NULL)
    total_invested      = models.FloatField()
    total_unit_initial  = models.FloatField()
    tree_type           = models.CharField(max_length=120)
    ica_register        = models.CharField(max_length=120, blank=True, null=True)
    n_hectares          = models.FloatField(validators=[MinValueValidator(0.0)])
    trees_left          = models.PositiveIntegerField(blank=True, null=True)
    project_link        = models.URLField(max_length=120, null=True, blank=True)
    payment_collection  = models.FloatField(null=True, blank=True)
    active              = models.BooleanField(default=True)
    image               = models.ImageField(verbose_name= "Imagen" ,upload_to="images/projects", null=True, blank=True)
    
    objects = ProjectManager()

    def save(self, *args, **kwargs):
        if self.trees_left is None:
            self.trees_left = self.n_trees
        super(Project, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    def __coordinates__(self):
        return self.coordinates

    def get_absolute_url(self):
        return reverse("project-detail", kwargs={"slug": self.slug})

    def delete(self, using=None, keep_parents=False):
        #import pdb; pdb.set_trace() 
        if self.image:
            self.image.storage.delete(self.image.name)
        super().delete()
        
    def get_price(self):
        return "{:.2f}".format(int(self.price_subscription.price or 0) /100)
    
    def get_trees_left_porcent(self):
        return 100 - ((self.trees_left * 100) / int(self.n_trees or 1)) 

class OrderItem(models.Model):
    order = models.ForeignKey("Order", related_name='items', on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default = 1)
    
    TYPE_INVERSION_CHOICES = [('M', 'Monthly subscription'), ('O', 'One payment')] 
    type_inversion = models.CharField(verbose_name='Inversion type', choices=TYPE_INVERSION_CHOICES, default='M', max_length=1) 
    
    
    def __Str__(self):
        return f"{self.quantity} x Trees in {self.project.name}"

    def get_raw_total_item_price(self):
        return self.quantity * int(self.project.price_subscription.price or 0) 
    
    def get_total_item_price(self):
        price = self.get_raw_total_item_price()
        return "{:.2f}".format(int(price or 0) /100)
    
    def get_label_type_choice(self):
        type = self.type_inversion
        return 'Monthly subscription' if type == 'M' else 'One Payment'
    
class Order(models.Model):
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE)
    bill = models.ForeignKey(Bill, related_name='bill', blank=True, null=True, on_delete=models.SET_NULL)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField(blank=True, null=True)
    ordered = models.BooleanField(default=False)
    
    billing_address = models.ForeignKey(
        Bill, related_name='billing_address', blank=True, null=True, on_delete=models.SET_NULL)
    shipping_address = models.ForeignKey(
        Bill, related_name='shipping_address', blank=True, null=True, on_delete=models.SET_NULL)
    
    def __str__(self):
        return self.reference_number
    
    @property
    def reference_number(self):
        return f"ORDER-{self.pk}"

    def get_raw_subtotal(self):
        total =  0
        for order_item in self.items.all():
            total += order_item.get_raw_total_item_price()
        return total
    def get_subtotal(self):
        subtotal = self.get_raw_subtotal()
        return "{:.2f}".format(int(subtotal or 0) /100)
    
    def get_raw_total(self):
        subtotal = self.get_raw_subtotal()
        discounts = 0
        impuestos = 0
        total =  subtotal - discounts + impuestos
        return total
    def get_total(self):
        total = self.get_raw_total()
        return "{:.2f}".format(int(total or 0) /100)
  
              
def pre_save_project_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = slugify(instance.name)

pre_save.connect(pre_save_project_receiver, sender= Project)      
    
class PercentageRecordQuerySet(models.query.QuerySet):
    def search(self, query):
        lookups = (Q(record_date__icontains=query) 

                  )

class PercentageRecordManager(models.Manager):
    def get_queryset(self):
        return PercentageRecordQuerySet(self.model, using=self._db)

    def get_by_id(self, id):
        qs = self.get_queryset().filter(pk=id) # Product.objects == self.get_queryset()
        if qs.count() == 1:
            return qs.first()
        return None

    def get_by_date(self, date):
        qs = self.get_queryset().filter(record_date=date)
        if qs.count() > 0:
            return qs
        return None
    
    def get_by_month(self, month):
        qs = self.get_queryset().filter(record_date__month=month)
        if qs.count() > 0:
            return qs
        return None

    def get_by_year(self, year):
        qs = self.get_queryset().filter(record_date__year=year)
        if qs.count() > 0:
            return qs
        return None

    def get_by_project_and_date(self, project, date):
        qs = self.get_queryset().filter(project=project).filter(record_date=date)
        if qs.count() == 1:
            return qs.first()
        return None

    def get_by_project_and_last_date(self, project):
        try:
            qs = self.get_queryset().filter(project=project).latest('record_date')
            return qs
        except:
            return None

class PercentageRecord(models.Model):
    project            = models.ForeignKey(Project, on_delete=models.CASCADE)
    
    record_date        = models.DateField(unique=True)
    growth_avg         = models.FloatField(validators=[MinValueValidator(0.0)])
    dch_avg            = models.FloatField(validators=[MinValueValidator(0.0)])
    volume_growth_avg  = models.FloatField(validators=[MinValueValidator(0.0)], null=True, blank=True)
    growth_pctg        = models.FloatField(validators=[MinValueValidator(0.0)])
    dch_pctg           = models.FloatField(validators=[MinValueValidator(0.0)])
    volume_growth_pctg = models.FloatField(validators=[MinValueValidator(0.0)], null=True, blank=True)
    total_unit_current = models.FloatField(validators=[MinValueValidator(0.0)], null=True, blank=True)
    profitability      = models.FloatField(validators=[MinValueValidator(0.0)], null=True, blank=True)
    project_value      = models.FloatField(null=True, blank=True)

    objects = PercentageRecordManager()

    class Meta:
        verbose_name = "Percentage record"
        verbose_name_plural = "Percentage records"
    
    def __str__(self):
        return self.project.name + '_' + str(self.pk)

class Plat(models.Model):
    plat_id = models.CharField(primary_key=True, max_length=50)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    n_trees = models.PositiveIntegerField()
    x1      = models.FloatField()
    x2      = models.FloatField()
    y1      = models.FloatField()
    y2      = models.FloatField()

    class Meta:
        verbose_name = "Plat"
        verbose_name_plural = "Plats"

    def __str__(self):
        return self.plat_id + ' ' + self.project.name 

class ProjectRecordQuerySet(models.query.QuerySet):
    def search(self, query):
        lookups = (Q(heigth__icontains=query) | 
                   Q(dch__icontains=query) |
                   Q(volume__icontains=query) |
                   Q(age__icontains=query)
                  )

class ProjectRecordManager(models.Manager):
    def get_queryset(self):
        return ProjectRecordQuerySet(self.model, using=self._db)
    
    def all(self):
        return self.get_queryset().objects.all()
    
    def get_by_id(self, id):
        qs = self.get_queryset().filter(id=id) # Product.objects == self.get_queryset()
        if qs.count() == 1:
            return qs.first()
        return None

    def get_by_plat(self, plat):
        qs = self.get_queryset().filter(plat=plat)
        if qs.count() >= 1:
            return qs
        return None
    
    def get_by_date(self, date):
        qs = self.get_queryset().filter(record_date=date)
        if qs.count() >= 1:
            return qs
        return None

    def get_by_project_and_date(self, project, date):
        qs = self.get_queryset().filter(plat__project=project).filter(record_date=date)
        if qs.count() >= 1:
            return qs
        return None
    
    def search(self, query):
        return self.get_queryset().search(query)

    
class ProjectTrackingRecord(models.Model):
    plat               = models.ForeignKey(Plat, on_delete=models.CASCADE)
    heigth             = models.FloatField(validators=[MinValueValidator(0.0)])
    dch                = models.FloatField(validators=[MinValueValidator(0.0)])
    volume             = models.FloatField(validators=[MinValueValidator(0.0)], blank=True, null=True)
    captured_co2       = models.FloatField(validators=[MinValueValidator(0.0)], blank=True, null=True)
    age                = models.FloatField(validators=[MinValueValidator(0.0)])
    record_date        = models.DateField()

    objects = ProjectRecordManager()
    
    class Meta:
        verbose_name = "Project record"
        verbose_name_plural = "Project records"

    def __str__(self):
        return self.plat.plat_id + '_' + self.plat.project.name + '_' + str(self.record_date)
    
    def save(self, *args, **kwargs):
        self.volume = ((math.pi / 4) * self.heigth) * self.dch**2
        self.captured_co2 = round((CO2_CONSUMPTION_PER_TREE_PER_DAY * self.plat.n_trees), 3)
        super(ProjectTrackingRecord, self).save(*args, **kwargs)

        last_growth_avg = None
        last_dch_avg    = None
        last_volume_avg = None
        
        days = timedelta(days=15)
        fifteen_days_ago = self.record_date - days
        #last_records = ProjectTrackingRecord.objects.get_by_date(fifteen_days_ago)

        plat_project = Project.objects.get_by_id(self.plat.project)
        last_percentage_record = PercentageRecord.objects.get_by_project_and_date(plat_project, fifteen_days_ago)
        
        if last_percentage_record is not None:
            last_growth_avg = last_percentage_record.growth_avg
            last_dch_avg    = last_percentage_record.dch_avg
            last_volume_avg = last_percentage_record.volume_growth_avg
        
        other_records = ProjectTrackingRecord.objects.get_by_project_and_date(self.plat.project, self.record_date)
        
        if other_records is not None:
            growth = [proj.heigth for proj in other_records]
            dch    = [proj.dch for proj in other_records]
            volume = [proj.volume for proj in other_records]

            current_mean_growth = mean(growth) # Mean heigth
            current_mean_dch    = mean(dch)
            current_mean_volume = mean(volume)

            if last_growth_avg is not None:
                growth_pctg = ((current_mean_growth - last_growth_avg) / current_mean_growth)
            else:
                growth_pctg = 0
            if last_dch_avg is not None:
                dch_pctg = ((current_mean_dch - last_dch_avg) / current_mean_dch)
            else:
                dch_pctg = 0
            if last_volume_avg is not None:
                volume_pctg = ((current_mean_volume - last_volume_avg) / current_mean_volume)

            total_unit_current = 0
            if plat_project.total_unit_initial is not None and volume_pctg is not None:
                total_unit_current = plat_project.total_unit_initial + (plat_project.total_unit_initial * volume_pctg)

            pr = PercentageRecord(project=plat_project, 
                                  record_date=self.record_date, 
                                  growth_avg=current_mean_growth, 
                                  dch_avg=current_mean_dch,
                                  volume_growth_avg=current_mean_volume,
                                  growth_pctg=growth_pctg * 100,
                                  dch_pctg=dch_pctg * 100,
                                  volume_growth_pctg=volume_pctg * 100,
                                  total_unit_current=total_unit_current) 
            pr.save()


