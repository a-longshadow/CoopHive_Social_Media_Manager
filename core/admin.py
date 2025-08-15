from django.contrib import admin
from .models import Campaign, Post, MediaAsset

@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ('name', 'platform', 'status', 'total_posts', 'total_engagement', 'start_date', 'end_date')
    list_filter = ('platform', 'status', 'created_at')
    search_fields = ('name', 'platform')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('content_preview', 'platform', 'status', 'likes', 'shares', 'comments', 'views', 'scheduled_time')
    list_filter = ('platform', 'status', 'created_at')
    search_fields = ('content', 'platform_post_id', 'hashtags')
    readonly_fields = ('created_at', 'updated_at')
    
    def content_preview(self, obj):
        return obj.content[:100] + "..." if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'Content'

@admin.register(MediaAsset)
class MediaAssetAdmin(admin.ModelAdmin):
    list_display = ('file_path', 'file_type', 'file_size', 'created_at')
    list_filter = ('file_type', 'created_at')
    search_fields = ('file_path',)
    readonly_fields = ('created_at',)
