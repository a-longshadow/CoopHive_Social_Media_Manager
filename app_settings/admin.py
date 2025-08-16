from django.contrib import admin
from django.utils.html import format_html
from .models import AppSetting


@admin.register(AppSetting)
class AppSettingAdmin(admin.ModelAdmin):
    """
    100% Database-First Settings Administration
    """
    
    list_display = [
        'key', 
        'value_preview', 
        'description_preview',
        'category_display',
        'is_configured',
        'updated_at'
    ]
    list_filter = ['updated_at', 'created_at']
    search_fields = ['key', 'description', 'value']
    readonly_fields = ['created_at', 'updated_at']
    
    def value_preview(self, obj):
        """Show a preview of the value with masking for sensitive data."""
        if not obj.value:
            return format_html('<span style="color: red;">❌ NOT SET</span>')
        
        # Mask sensitive values
        sensitive_keys = [
            'SECRET_KEY', 'PASSWORD', 'CLIENT_SECRET', 'API_KEY', 'TOKEN'
        ]
        
        if any(sensitive in obj.key.upper() for sensitive in sensitive_keys):
            if len(obj.value) > 10:
                return format_html('<span style="color: green;">🔒 ••••••••••••</span>')
            else:
                return format_html('<span style="color: orange;">⚠️ Too Short</span>')
        
        # Show preview for non-sensitive values
        preview = obj.value[:50]
        if len(obj.value) > 50:
            preview += '...'
        return format_html('<span style="color: green;">{}</span>', preview)
    
    value_preview.short_description = 'Value Status'
    
    def description_preview(self, obj):
        """Show a truncated description."""
        if not obj.description:
            return '-'
        preview = obj.description[:100]
        if len(obj.description) > 100:
            preview += '...'
        return preview
    
    description_preview.short_description = 'Description'
    
    def category_display(self, obj):
        """Display category based on key name."""
        key_upper = obj.key.upper()
        
        if 'SECRET' in key_upper or 'PASSWORD' in key_upper or 'TOKEN' in key_upper:
            return format_html('<span style="color: red;">🔐 Security</span>')
        elif 'EMAIL' in key_upper:
            return format_html('<span style="color: blue;">📧 Email</span>')
        elif 'GOOGLE' in key_upper or 'OAUTH' in key_upper:
            return format_html('<span style="color: green;">🔐 OAuth</span>')
        elif 'DOMAIN' in key_upper:
            return format_html('<span style="color: purple;">🌐 Access Control</span>')
        elif 'DEBUG' in key_upper:
            return format_html('<span style="color: orange;">🔧 Core</span>')
        else:
            return format_html('<span style="color: gray;">⚙️ General</span>')
    
    category_display.short_description = 'Category'
    
    def is_configured(self, obj):
        """Check if the setting is properly configured."""
        if not obj.value or obj.value.strip() == '':
            return format_html('<span style="color: red;">❌ Empty</span>')
        
        # Special checks for boolean values
        bool_settings = ['DEBUG', 'DOMAIN_RESTRICTION_ENABLED', 'GOOGLE_VERIFICATION_ENABLED', 'EMAIL_USE_TLS', 'EMAIL_USE_SSL']
        if obj.key.upper() in bool_settings:
            if obj.value.lower() in ['true', 'false']:
                return format_html('<span style="color: green;">✅ Valid</span>')
            else:
                return format_html('<span style="color: orange;">⚠️ Invalid Boolean</span>')
        
        # Special checks for email port
        if obj.key.upper() == 'EMAIL_PORT':
            try:
                port = int(obj.value)
                if 1 <= port <= 65535:
                    return format_html('<span style="color: green;">✅ Valid</span>')
                else:
                    return format_html('<span style="color: red;">❌ Invalid Port</span>')
            except ValueError:
                return format_html('<span style="color: red;">❌ Not Number</span>')
        
        return format_html('<span style="color: green;">✅ Set</span>')
    
    is_configured.short_description = 'Status'
    
    def value_preview(self, obj):
        if obj.value:
            return obj.value[:100] + "..." if len(obj.value) > 100 else obj.value
        return "(empty)"
    value_preview.short_description = 'Value'
