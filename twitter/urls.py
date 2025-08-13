from django.urls import path
from . import views

app_name = 'twitter'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Posts
    path('posts/', views.post_list, name='post_list'),
    path('posts/new/', views.post_create, name='post_create'),
    path('posts/<int:pk>/', views.post_detail, name='post_detail'),
    path('posts/<int:pk>/edit/', views.post_edit, name='post_edit'),
    path('posts/<int:pk>/delete/', views.post_delete, name='post_delete'),
    
    # Media handling
    path('media/upload/', views.media_upload, name='media_upload'),
    path('media/<int:pk>/delete/', views.media_delete, name='media_delete'),
    
    # API endpoints
    path('api/preview/', views.generate_preview, name='generate_preview'),
    path('api/schedule/', views.schedule_tweet, name='schedule_tweet'),
    path('api/post/', views.post_tweet, name='post_tweet'),
    
    # Analytics
    path('analytics/', views.analytics, name='analytics'),
    path('analytics/export/', views.export_analytics, name='export_analytics'),
]
