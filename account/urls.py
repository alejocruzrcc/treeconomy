from django.urls import path, include, re_path

from account.models import ProjectByInvestor
from . import views
from django.contrib.auth import views as auth_views
from account.forms import EmailValidationOnForgotPassword
from django.contrib.auth.decorators import login_required


urlpatterns = [
    #postviews
    #path('login/',views.user_login,name='login'),
    
    #path('login/',auth_views.LoginView.as_view(),name='login'),
    #path('logout/',auth_views.LogoutView.as_view(),name='logout'),
    # #change password
    #path('password_change/',auth_views.PasswordChangeView.as_view(),name='password_change'),
    #path('password_change/done/',auth_views.PasswordChangeDoneView.as_view(),name='password_change_done'),
    # #reset password
    #path('password_reset/',auth_views.PasswordResetView.as_view(),name='password_reset'),
    #path('password_reset/done/',auth_views.PasswordResetDoneView.as_view(),name='password_reset_done'),
    #path('reset/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(),name='password_reset_confirm'),
    #path('reset/done/',auth_views.PasswordResetCompleteView.as_view(),name='password_reset_complete'),
    path('',include('django.contrib.auth.urls')),
    path('register/',views.register,name='register'),
    path('profile',views.profile,name='profile'),
    path('edit/',views.edit,name='edit'),
    path('activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.activate_account, name='activate'),
    path('account/password_reset/', auth_views.PasswordResetView.as_view(form_class=EmailValidationOnForgotPassword), name='password_reset'),
    path('subscription/',  login_required(views.create_subscription) , name='create_subscription'),
    #path('your-projects/', ProjectByInvestorView.as_view(), name='projectsbyinvestor'),
    #path('projectsbyinvestor/<int:pk>', ProjectByInvestorDetailView.as_view(), name='project-investor-detail')

]