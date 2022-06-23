from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
import datetime
from django_countries.fields import CountryField
from phonenumber_field.modelfields import PhoneNumberField
from projects.models import Project, Subscription, Pricing
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
import stripe


DEFAULT_ACTIVATION_DAYS = getattr(settings, 'DEFAULT_ACTIVATION_DAYS', 7)
DAYS_PER_YEAR = 365
TREES_PER_HECTARE = 500
CO2_CONSUMPTION_PER_HECTARE_PER_YEAR = 35000
CO2_CONSUMPTION_PER_TREE_PER_YEAR = (CO2_CONSUMPTION_PER_HECTARE_PER_YEAR / TREES_PER_HECTARE)
CO2_CONSUMPTION_PER_TREE_PER_DAY = (CO2_CONSUMPTION_PER_TREE_PER_YEAR / DAYS_PER_YEAR)



class Profile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    stripe_customer_id = models.CharField(max_length=50)
    # ROLES DE USUARIO 
    VISITOR = 1 ## Unicamente ve información y dahboard de ejemplo
    ONETIME_INVESTOR = 2 ## Es inversionista de pago único
    SUBSCRIPTION_INVESTOR = 3 # Es inversionista con subscripción
    ADMIN = 4 # Administrador

    ROLE_CHOICES = [
        (VISITOR , 'Visitor'),
        (ONETIME_INVESTOR, 'One Time Investment'), 
        (SUBSCRIPTION_INVESTOR, 'Subscription Investment'),
        (ADMIN , 'Admin'),
        ]
    role = models.PositiveSmallIntegerField(choices=ROLE_CHOICES, blank=True, null=True)
    ## Género
    GENDER_MALE = 1
    GENDER_FEMALE = 2
    GENDER_CHOICES = [(GENDER_MALE, 'Male'), (GENDER_FEMALE, 'Female'),]
   
    # Campos del perfil 
    
    #gender         = models.IntegerField(choices=GENDER_CHOICES, blank=True, null=True)
    country        = CountryField(default="Co")
    city           = models.CharField(max_length=50, blank=True, null=True, verbose_name = "Ciudad")
    state          = models.CharField(max_length=50, blank=True, null=True)
    adress         = models.CharField(max_length=50, blank=True, null=True)
    zipcode        = models.CharField(max_length=100, blank=True, null=True)
    phone          = PhoneNumberField(blank=True, null=True)
    date_of_birth  = models.DateField(blank=True, null=True)
    rut            = models.CharField(max_length=100, blank=True, null=True)
    tax_register   = models.CharField(max_length=50, blank=True, null=True)
    facebook       = models.URLField(max_length=200, blank=True, null=True)
    instagram      = models.URLField(max_length=200, blank=True, null=True)
    twitter        = models.URLField(max_length=200, blank=True, null=True)
    web_domine     = models.URLField(max_length=200, blank=True, null=True)
    photo          = models.ImageField(upload_to='images/users/%Y/%m/%d',blank=True, null=True)
    
    @receiver(post_save, sender=User) #add this
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)

    @receiver(post_save, sender=User) #add this
    def save_user_profile(sender, instance, **kwargs):
        instance.profile.save()
        
    def __str__(self):
        return f'Perfil para usuario {self.user.username}'
    
    
    
    class Meta:
        verbose_name_plural=u'Perfiles de Usuario'
        
class CommissionAgent(User):
    people_related = models.PositiveIntegerField()
    percentage_per_person = models.FloatField()

    class Meta:
        verbose_name = "Commission agent"
        verbose_name_plural = "Commission agents"

    def __str__(self):
        return self.name + " " + self.last_name


class ProjectByInvestorQuerySet(models.query.QuerySet):
    def active(self):
        return self.filter(active=True)

    def search(self, query):
        lookups = (Q(investor__icontains=query)         | 
                   Q(project__icontains=query)          |
                   Q(commission_agent__icontains=query) |
                   Q(n_trees__icontains=query)           |
                   Q(coordinates__icontains=query)
                  )

class ProjectByInvestorManager(models.Manager):
    def get_queryset(self):
        return ProjectByInvestorQuerySet(self.model, using=self._db)
    
    def all(self):
        return self.get_queryset().active()
    
    def get_by_id(self, id):
        qs = self.get_queryset().filter(id=id) # Product.objects == self.get_queryset()
        if qs.count() == 1:
            return qs.first()
        return None

    def get_by_investor(self, investor_id):
        qs = self.get_queryset().select_related('project').filter(investor=investor_id) #filter(investor=investor_id)
        if qs.count() >= 1:
            return qs
        return None
    
    def get_by_project(self, project_id):
        qs = self.get_queryset().filter(investor=project_id)
        if qs.count() >= 1:
            return qs
        return None
    
    def search(self, query):
        return self.get_queryset().active().search(query)

class ProjectByInvestor(models.Model):
    investor         = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_investor")
    project          = models.ForeignKey(Project, on_delete=models.CASCADE)
    commission_agent = models.ForeignKey(CommissionAgent, null=True, blank=True, on_delete=models.CASCADE, related_name="user_commission_agent")
    n_trees          = models.PositiveIntegerField()
    total_price      = models.FloatField(validators=[MinValueValidator(0.0)])
    unit_price       = models.FloatField(validators=[MinValueValidator(0.0)])
    tax              = models.FloatField(validators=[MinValueValidator(0.0)])
    date             = models.DateField(auto_now=False, auto_now_add=False)
    next_payment     = models.DateField(auto_now=False, auto_now_add=False)
    coordinates      = models.CharField(max_length=50)
    co2_consumption  = models.FloatField(validators=[MinValueValidator(0.0)], null=True, blank=True)
    active           = models.BooleanField(default=True)

    objects = ProjectByInvestorManager()

    class Meta:
        verbose_name = "Project by investor"
        verbose_name_plural = "Projects by investor"

    def save(self, *args, **kwargs):
        proj =  get_object_or_404(Project, slug=self.project.slug)

        if self.co2_consumption is None:
            self.co2_consumption = round((CO2_CONSUMPTION_PER_TREE_PER_DAY * self.n_trees), 3)

        if self.n_trees <= proj.trees_left:
            super(ProjectByInvestor, self).save(*args, **kwargs)
            proj.trees_left -= self.n_trees
            if proj.trees_left == 0: proj.active = False
            proj.save()
        else:
            print("There are not enough trees to buy in this project")
    def __str__(self):
        return str(self.pk) + "_" + self.investor.profile.rut + "_" + self.project.name

    def get_absolute_url(self):
        return reverse("project-investor-detail", kwargs={"pk": self.pk})

@receiver(post_save, sender=User)
def post_email_confirmed(sender, instance, created, **kwargs):
    print("entrooo")
    if created:
        user = instance
        free_trial_pricing = Pricing.objects.get(name='Free')
        
        subscription = Subscription.objects.create(
            user=user,
            pricing=free_trial_pricing
        )

        #Crear cliente en stripe
        stripe_customer = stripe.Customer.create(
            email=user.email
        )
        
        stripe_subscription = stripe.Subscription.create(
            customer=stripe_customer["id"],
            items=[{'price': settings.STRIPE_FREE_PRICE}],
            trial_period_days=20
        )

        subscription.status=stripe_subscription["status"]
        subscription.stripe_subscription_id = stripe_subscription["id"]
        subscription.save()
        profile = Profile.objects.get(user_id=user.id)
        profile.stripe_customer_id=stripe_customer["id"]
        profile.save()

