# Database-Only Settings App

We'll create a dedicated Django app called `app_settings` for managing all application settings purely in the database. Here's the implementation plan:

## Core Components

### AppSetting Model
```python
# app_settings/models.py
from django.db import models

class AppSetting(models.Model):
    key = models.CharField(max_length=100, unique=True, db_index=True)
    value = models.TextField(blank=True)
    description = models.TextField(blank=True, help_text="What this setting does")
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Application Setting"
        verbose_name_plural = "Application Settings"
        ordering = ["key"]

    def __str__(self):
        return self.key


### App Configuration
```python
# app_settings/apps.py
from django.apps import AppConfig

class AppSettingsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_settings'
    verbose_name = 'Application Settings'

### Settings Manager
```python
# app_settings/settings.py
from django.core.exceptions import ObjectDoesNotExist
from .models import AppSetting

class SettingsManager:
    @staticmethod
    def get(key: str) -> str:
        """Get a setting value from the database."""
        try:
            setting = AppSetting.objects.get(key=key)
            return setting.value
        except ObjectDoesNotExist:
            raise KeyError(f"Setting '{key}' does not exist in database")

### Admin Interface
```python
# app_settings/admin.py
from django.contrib import admin
from .models import AppSetting

@admin.register(AppSetting)
class AppSettingAdmin(admin.ModelAdmin):
    list_display = ['key', 'value', 'updated_at']
    search_fields = ['key', 'value', 'description']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        (None, {
            'fields': ('key', 'value', 'description')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

### Management Commands
```python
# app_settings/management/commands/init_settings.py
from django.core.management.base import BaseCommand
from app_settings.models import AppSetting

class Command(BaseCommand):
    help = 'Initialize application settings with default values'

    def handle(self, *args, **options):
        settings_to_create = [
            {
                'key': 'GOOGLE_OAUTH_CLIENT_ID',
                'value': '',
                'description': 'Google OAuth Client ID for authentication'
            },
            # Add other settings as needed
        ]

        for setting in settings_to_create:
            AppSetting.objects.get_or_create(
                key=setting['key'],
                defaults={
                    'value': setting['value'],
                    'description': setting['description']
                }
            )
### Usage in Django Code
```python
# In any Django module where settings are needed:
from app_settings.settings import SettingsManager

# Get a setting value
try:
    oauth_client_id = SettingsManager.get('GOOGLE_OAUTH_CLIENT_ID')
except KeyError:
    # Handle missing setting appropriately
    pass

### Implementation Steps

1. Create the app:
   ```bash
   python manage.py startapp app_settings
   ```

2. Add to INSTALLED_APPS:
   ```python
   INSTALLED_APPS = [
       ...
       'app_settings',
   ]
   ```

3. Create initial migrations:
   ```bash
   python manage.py makemigrations app_settings
   ```

4. Apply migrations:
   ```bash
   python manage.py migrate
   ```

5. Initialize settings:
   ```bash
   python manage.py init_settings
   ```

### Settings to Store

- Authentication Settings
  - GOOGLE_OAUTH_CLIENT_ID
  - GOOGLE_OAUTH_CLIENT_SECRET
  
- Email Configuration
  - EMAIL_HOST_USER
  - EMAIL_HOST_PASSWORD
  - DEFAULT_FROM_EMAIL
  
- Domain Settings
  - ALLOWED_HOSTS
  - DOMAIN_RESTRICTION_ENABLED
  - ALLOWED_DOMAIN


### Key Features

1. Pure Database Storage
   - All settings stored in database only
   - No environment variable fallbacks
   - No default values in code
   
2. Admin Interface
   - Easy-to-use Django admin interface
   - Search and filter capabilities
   - Audit trail through timestamps
   
3. Secure Access
   - Settings accessed through SettingsManager
   - Exception handling for missing settings
   - Database-level constraints

4. Migration-Friendly
   - Clear migration path
   - Settings initialization command
   - No environment dependencies

5. Maintainable
   - Clean separation of concerns
   - Clear error messages
   - Easy to extend

### Example Usage

```python
# In your Django views/services:
from app_settings.settings import SettingsManager

def some_view(request):
    try:
        oauth_id = SettingsManager.get('GOOGLE_OAUTH_CLIENT_ID')
        oauth_secret = SettingsManager.get('GOOGLE_OAUTH_CLIENT_SECRET')
        # Use the settings...
    except KeyError as e:
        # Handle missing settings
        pass
```

Would you like me to proceed with implementing any specific part of this plan?