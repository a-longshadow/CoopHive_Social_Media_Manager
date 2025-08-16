# 100% Database-First Settings Implementation Guide

## Overview

This implementation provides a **100% compliant** database-first, environment variable second approach for application settings, following the Variable Update Plan requirements.

## Architecture

### Priority Order
1. **Database** (AppSetting model) - PRIMARY source
2. **Environment Variables** - Fallback only
3. **Fail Securely** - NO hardcoded defaults (except super admin emails)

### Only Hardcoded Values Allowed
- Super Admin Emails: `joe@coophive.network`, `levi@coophive.network`

## Implementation Components

### 1. Core Manager (`app_settings/manager.py`)
```python
from app_settings.manager import settings_manager

# Get required setting (fails if not found)
secret_key = settings_manager.get('SECRET_KEY', required=True)

# Get optional setting with type casting
debug_mode = settings_manager.get_bool('DEBUG', required=False)

# Set setting in database
settings_manager.set('NEW_SETTING', 'value', 'Description')
```

### 2. Django Settings Helper (`app_settings/django_settings.py`)
```python
from app_settings.django_settings import get_credential_setting

# Use in settings.py
SECRET_KEY = get_credential_setting('SECRET_KEY', required=True)
DEBUG = get_credential_setting('DEBUG', value_type=bool, required=True)
```

### 3. Management Commands

#### Initialize Settings
```bash
# Create all settings with empty values (100% secure)
python manage.py init_settings_new

# Create settings AND super admin accounts
python manage.py init_settings_new --create-super-admins

# Force update existing settings
python manage.py init_settings_new --force
```

### 4. Admin Interface
- Comprehensive settings management at `/admin/app_settings/appsetting/`
- Security masking for sensitive values
- Validation for boolean and numeric values
- Category-based organization
- Configuration status tracking

## Settings Configuration

### Critical Settings (MUST be configured)

#### Security Settings
- `SECRET_KEY` - Django cryptographic signing key
- `DEBUG` - Debug mode (True/False)

#### Google OAuth Settings
- `GOOGLE_OAUTH_CLIENT_ID` - OAuth client ID
- `GOOGLE_OAUTH_CLIENT_SECRET` - OAuth client secret

#### Email Settings
- `EMAIL_HOST` - SMTP server (e.g., smtp.gmail.com)
- `EMAIL_PORT` - SMTP port (587 for TLS, 465 for SSL)
- `EMAIL_USE_TLS` - Use TLS (True/False)
- `EMAIL_USE_SSL` - Use SSL (True/False)  
- `EMAIL_HOST_USER` - SMTP username
- `EMAIL_HOST_PASSWORD` - SMTP password
- `DEFAULT_FROM_EMAIL` - From email address

#### Access Control Settings
- `DOMAIN_RESTRICTION_ENABLED` - Enable domain restriction (True/False)
- `ALLOWED_DOMAIN` - Allowed email domain
- `GOOGLE_VERIFICATION_ENABLED` - Enable Google verification (True/False)

## Configuration Methods

### Method 1: Environment Variables (Recommended for Production)
```bash
export SECRET_KEY="your-secret-key-here"
export DEBUG="False"
export GOOGLE_OAUTH_CLIENT_ID="your-client-id"
# ... etc
```

### Method 2: Database Configuration (via Django Admin)
1. Run migrations: `python manage.py migrate`
2. Initialize settings: `python manage.py init_settings_new`
3. Go to `/admin/app_settings/appsetting/`
4. Configure each setting value

### Method 3: Programmatic Configuration
```python
from app_settings.manager import settings_manager

settings_manager.set('SECRET_KEY', 'your-secret-key')
settings_manager.set('DEBUG', 'False')
settings_manager.set('EMAIL_HOST', 'smtp.gmail.com')
```

## Deployment Workflow

### Local Development
1. Set environment variables in `.env` file
2. Run: `python manage.py init_settings_new --create-super-admins`
3. Configure additional settings via admin interface

### Production (Railway)
1. Set critical environment variables in Railway dashboard:
   - `SECRET_KEY`
   - `DEBUG=False`
   - Database credentials
2. Deploy application
3. Run post-deploy command: `python manage.py init_settings_new`
4. Configure remaining settings via admin interface

## Security Features

### Fail-Safe Defaults
- NO hardcoded secrets or credentials
- Empty settings require explicit configuration
- Clear error messages for missing required settings

### Admin Interface Security
- Sensitive values are masked in list view
- Validation for boolean and numeric values
- Audit trail with timestamps
- Category-based organization

### Environment Detection
- Automatic fallback during database unavailability
- Graceful handling during migrations
- Clear error messages for misconfiguration

## Testing Configuration

```python
# Test database-first approach
python manage.py shell

from app_settings.manager import settings_manager

# Check if setting exists
print(settings_manager.exists('SECRET_KEY'))

# Get all settings
print(settings_manager.get_all_settings())

# Test required setting
try:
    secret = settings_manager.get('SECRET_KEY', required=True)
    print("SECRET_KEY is configured")
except Exception as e:
    print(f"SECRET_KEY missing: {e}")
```

## Troubleshooting

### Setting Not Found Errors
```
ImproperlyConfigured: Required setting 'SECRET_KEY' not found
```
**Solution**: Set via environment variable or database admin interface

### Database Connection Errors During Startup
- Settings helper gracefully falls back to environment variables
- Initialize settings after first successful migration

### Invalid Boolean Values
- Use exactly "True" or "False" (case insensitive)
- Admin interface validates boolean settings

## Migration from Hardcoded Settings

1. **Identify** all hardcoded settings in `settings.py`
2. **Replace** with `get_credential_setting()` calls
3. **Initialize** settings: `python manage.py init_settings_new`
4. **Configure** values via environment or admin interface
5. **Test** all functionality
6. **Deploy** with confidence

## Best Practices

1. **Always use environment variables for secrets in production**
2. **Use database for non-secret configuration**
3. **Initialize settings on every deployment**
4. **Monitor configuration completeness via admin interface**
5. **Document required settings for new environments**

This implementation ensures 100% compliance with database-first principles while maintaining security and operational flexibility.
