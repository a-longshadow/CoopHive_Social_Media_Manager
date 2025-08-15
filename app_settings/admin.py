from django.contrib import admin
from .models import AppSetting

@admin.register(AppSetting)
class AppSettingAdmin(admin.ModelAdmin):
    list_display = ('key', 'value_preview', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('key', 'value', 'description')
    readonly_fields = ('created_at', 'updated_at')
    
    def value_preview(self, obj):
        if obj.value:
            return obj.value[:100] + "..." if len(obj.value) > 100 else obj.value
        return "(empty)"
    value_preview.short_description = 'Value'
