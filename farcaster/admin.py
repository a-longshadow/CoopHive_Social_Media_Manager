from django.contrib import admin
from .models import FarcasterPost

@admin.register(FarcasterPost)
class FarcasterPostAdmin(admin.ModelAdmin):
    list_display = ('campaign', 'status', 'channel', 'recasts', 'likes', 'scheduled_time')
    list_filter = ('status', 'channel')
    search_fields = ('content', 'campaign__name', 'cast_hash')
    readonly_fields = ('recasts', 'watches', 'reactions')
