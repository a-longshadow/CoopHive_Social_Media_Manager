from django.urls import path
from . import views

app_name = 'accounts'  # Change from 'user_account_manager' to 'accounts' to match code expectations

urlpatterns = [
    # Email-based authentication
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    path('verify/', views.verify, name='verify'),
    
    # Google OAuth verification
    path('google/verify/', views.google_verify, name='google-verify'),
    path('domain-breach/', views.domain_breach_redirect, name='domain-breach'),
    
    # Password reset (if needed)
    path('password/reset/', views.reset_request, name='reset'),
    path('password/verify/', views.reset_verify, name='reset-verify'),
]
