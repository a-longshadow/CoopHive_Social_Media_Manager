from django.urls import path
from . import views

app_name = 'farcaster'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('casts/', views.cast_list, name='cast_list'),
    path('casts/new/', views.cast_create, name='cast_create'),
    path('casts/<int:pk>/', views.cast_detail, name='cast_detail'),
    path('casts/<int:pk>/edit/', views.cast_edit, name='cast_edit'),
    path('casts/<int:pk>/delete/', views.cast_delete, name='cast_delete'),
    path('media/upload/', views.media_upload, name='media_upload'),
    path('media/<int:pk>/delete/', views.media_delete, name='media_delete'),
    path('api/preview/', views.generate_preview, name='generate_preview'),
    path('api/schedule/', views.schedule_cast, name='schedule_cast'),
    path('api/publish/', views.publish_cast, name='publish_cast'),
    path('analytics/', views.analytics, name='analytics'),
    path('analytics/export/', views.export_analytics, name='export_analytics'),
]
