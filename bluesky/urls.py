from django.urls import path
from . import views

app_name = 'bluesky'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
]
