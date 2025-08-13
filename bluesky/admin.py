from django.contrib import admin
from .models import BlueskyPost

@admin.register(BlueskyPost)
class BlueskyPostAdmin(admin.ModelAdmin):
    list_display = ('campaign', 'status', 'reposts', 'likes', 'scheduled_time')
    list_filter = ('status',)
    search_fields = ('content', 'campaign__name', 'uri', 'rkey')
    readonly_fields = ('reposts', 'likes', 'self_labels')
