from django.contrib import admin
from .models import LinkedInPost

@admin.register(LinkedInPost)
class LinkedInPostAdmin(admin.ModelAdmin):
    list_display = ('campaign', 'status', 'visibility', 'impressions', 'engagement_rate', 'scheduled_time')
    list_filter = ('status', 'visibility')
    search_fields = ('content', 'campaign__name', 'company_page_id')
    readonly_fields = ('impressions', 'click_through_rate', 'engagement_rate')
