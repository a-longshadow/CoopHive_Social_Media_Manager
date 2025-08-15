from django.db import models


class SettingsManager:
    """Database-first settings manager"""
    
    @staticmethod
    def get_setting(key, default=None):
        """Get a setting value from database"""
        try:
            setting = AppSetting.objects.get(key=key)
            return setting.value
        except AppSetting.DoesNotExist:
            return default
    
    @staticmethod
    def set_setting(key, value):
        """Set a setting value in database"""
        setting, created = AppSetting.objects.get_or_create(
            key=key,
            defaults={'value': str(value), 'description': f'Setting for {key}'}
        )
        if not created:
            setting.value = str(value)
            setting.save()
        return setting


class AppSetting(models.Model):
    """Database-backed application settings"""
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Setting'
        verbose_name_plural = 'Settings'
        ordering = ['key']
    
    def __str__(self):
        return f"{self.key}: {self.value[:50]}{'...' if len(str(self.value)) > 50 else ''}"
