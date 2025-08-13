from django.contrib import admin
from .models import Campaign, Post, MediaAsset

@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ('name', 'platform', 'status', 'total_posts', 'total_engagement', 'created_at')
    list_filter = ('platform', 'status')
    search_fields = ('name', 'description')
    ordering = ('-created_at',)

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('campaign', 'platform', 'status', 'scheduled_time', 'published_time')
    list_filter = ('platform', 'status')
    search_fields = ('content', 'campaign__name')
    ordering = ('-created_at',)

@admin.register(MediaAsset)
class MediaAssetAdmin(admin.ModelAdmin):
    list_display = ('file_type', 'original_filename', 'post', 'created_at')
    list_filter = ('file_type',)
    search_fields = ('original_filename', 'post__content')
