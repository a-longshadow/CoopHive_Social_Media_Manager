from django.urls import path
from . import views

app_name = 'user_account_manager'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    path('verify/', views.verify, name='verify'),
]
