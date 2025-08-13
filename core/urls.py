from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Homepage
    path('', views.home, name='home'),
]
