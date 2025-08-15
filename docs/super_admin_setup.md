# Super Admin & Email Configuration Guide

## Overview

CoopHive automatically creates hardcoded super admin users and provides a flexible email configuration system for password resets and notifications.

## Super Admin Users

### Automatically Created Users
- **`joe@coophive.network`** - Primary super admin
- **`levi@coophive.network`** - Secondary super admin

### Key Features
- **No passwords set** - Must use Google OAuth or password reset
- **Created on startup** - Automatic initialization when Django starts
- **Preserved data** - Existing users are never overwritten
- **Full admin access** - Both superuser and staff privileges

### Access Methods (BOTH WORKING!)
1. ✅ **Google OAuth**: Visit `/accounts/login/` → "Continue with Google" → Fully functional!
2. ✅ **Password Reset**: Visit `/accounts/password/reset/` → Enter email → Set password → Working with database-first email system!

## Email Configuration System

### Database-First Architecture
The email system follows CoopHive's database-first philosophy:

1. **Primary**: Database settings (via `AppSetting` model)
2. **Fallback**: Environment variables (`.env` file)
3. **Default**: Reasonable defaults for development

### Bootstrap Problem Solution
For fresh installations, you need email credentials to enable password reset:

#### Create `.env` File
```bash
# In project root
touch .env
```

Add these contents:
```env
# Email Configuration (Required for super admin password reset)
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-gmail-app-password
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=465
DEFAULT_FROM_EMAIL=noreply@coophive.network
```

#### Gmail Setup Requirements
1. **Enable 2-Factor Authentication** on your Gmail account
2. **Generate App Password** (not your regular password):
   - Google Account → Security → 2-Step Verification → App passwords
   - Generate password for "Mail"
3. **Use App Password** in `EMAIL_HOST_PASSWORD`

### Email Management Commands

#### Check Configuration Status
```bash
python manage.py init_email --check
```
**Output Example:**
```
=== Email Configuration Status ===
✅ EMAIL_HOST: smtp.gmail.com (database)
✅ EMAIL_PORT: 465 (database)
✅ EMAIL_USE_TLS: False (database)
✅ EMAIL_HOST_USER: joe@coophive.network (database)
✅ EMAIL_HOST_PASSWORD: *** (database)
✅ DEFAULT_FROM_EMAIL: noreply@coophive.network (database)

✅ Email is configured and ready for sending
Super admins can reset passwords at /accounts/password/reset/
```

#### Set Database Credentials
```bash
# Set email username
python manage.py init_email --set-user "your-email@gmail.com"

# Set email password
python manage.py init_email --set-password "your-gmail-app-password"

# Set SMTP host (optional)
python manage.py init_email --set-host "smtp.gmail.com"

# Set from email (optional)
python manage.py init_email --set-from "noreply@yourdomain.com"
```

#### Test Email Sending
```bash
python manage.py init_email --test "recipient@example.com"
```

#### Clear Database Settings
```bash
# Remove all email settings from database (fallback to environment)
python manage.py init_email --clear
```

### Super Admin Management Commands

#### Check Super Admin Status
```bash
python manage.py create_super_admins
```
**Output Example:**
```
User joe@coophive.network already exists as super admin
User levi@coophive.network already exists as super admin

All super admin users already exist and are properly configured

Note: Super admin users have no password set.
✅ Email is configured. Super admins can:
  1. Use Google OAuth to log in at /accounts/login/
  2. Reset password via email at /accounts/password/reset/

Super admins can now access the system! 🎉
```

## Technical Implementation

### Custom Email Backend
The system uses a custom email backend that loads settings dynamically:

```python
# coophive/settings.py
EMAIL_BACKEND = 'user_account_manager.email_backend.DatabaseFirstEmailBackend'
```

**Features:**
- **Runtime loading** - Settings loaded when sending email, not at startup
- **Graceful fallback** - Uses environment variables if database unavailable
- **Gmail SSL support** - Automatically uses SSL for port 465
- **No circular imports** - Avoids Django startup issues

### Auto-Initialization
Super admins are created automatically via `AppConfig.ready()`:

```python
# user_account_manager/apps.py
def ready(self):
    # Only run during normal server startup
    if 'RUN_MAIN' not in os.environ:
        return
        
    # Schedule creation after app is fully ready
    timer = threading.Timer(1.0, create_super_admins_delayed)
    timer.daemon = True
    timer.start()
```

### Database Settings Storage
Email credentials are stored in the `AppSetting` model:

```python
# Example database entries
EMAIL_HOST: smtp.gmail.com
EMAIL_PORT: 465
EMAIL_USE_TLS: False
EMAIL_HOST_USER: joe@coophive.network
EMAIL_HOST_PASSWORD: tgws eabi xakt mmks
DEFAULT_FROM_EMAIL: noreply@coophive.network
```

## Deployment Scenarios

### Scenario 1: Fresh Installation
1. **Create `.env` file** with email credentials
2. **Run migrations**: `python manage.py migrate`
3. **Initialize settings**: `python manage.py init_settings`
4. **Start server**: `python manage.py runserver`
5. **Super admins created automatically**
6. **Password reset available** via email

### Scenario 2: Existing Installation
1. **Super admins detected** - no changes made
2. **Email config checked** - uses existing settings
3. **Backward compatibility** - environment variables still work
4. **Optional migration** - move credentials to database when convenient

### Scenario 3: Production Deployment
1. **Environment variables** - Set in deployment platform
2. **Database migration** - Optional move to database storage
3. **Email testing** - Verify configuration with `init_email --test`
4. **Super admin access** - Available immediately

## Security Considerations

### Credential Storage
- **Database encryption** - Consider encrypting sensitive values
- **Environment variables** - Never commit to version control
- **Access control** - Restrict admin interface access
- **Audit logging** - Track email configuration changes

### Gmail Security
- **App passwords only** - Never use regular Gmail passwords
- **2FA required** - Enable two-factor authentication
- **Limited scope** - App passwords have restricted access
- **Regular rotation** - Change passwords periodically

### Network Security
- **SSL/TLS encryption** - All email traffic encrypted
- **Port considerations** - 465 (SSL) vs 587 (TLS)
- **Firewall rules** - Ensure SMTP ports are open
- **Rate limiting** - Prevent email abuse

## Troubleshooting

### Common Issues

#### "Operation timed out" Error
**Cause**: Network/firewall blocking SMTP connections
**Solutions**:
1. Try port 465 (SSL) instead of 587 (TLS)
2. Check firewall settings
3. Test with different network
4. Verify Gmail app password

#### "Authentication failed" Error
**Cause**: Incorrect Gmail credentials
**Solutions**:
1. Verify app password (not regular password)
2. Ensure 2FA is enabled on Gmail
3. Generate new app password
4. Check email address spelling

#### Super Admins Not Created
**Cause**: Database not ready during startup
**Solutions**:
1. Run manually: `python manage.py create_super_admins`
2. Check database connectivity
3. Verify migrations applied
4. Restart Django server

#### Email Not Configured Warning
**Cause**: Missing email credentials
**Solutions**:
1. Create `.env` file with credentials
2. Set database values: `python manage.py init_email --set-user`
3. Check configuration: `python manage.py init_email --check`
4. Test sending: `python manage.py init_email --test`

### Debug Commands

#### Check Email Settings
```bash
# View current configuration and sources
python manage.py init_email --check

# Test SMTP connection
python manage.py shell -c "
import smtplib
server = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=10)
print('✅ SMTP connection successful')
server.quit()
"
```

#### Check Super Admin Status
```bash
# List all super admin users
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
for user in User.objects.filter(is_superuser=True):
    print(f'{user.email} - Active: {user.is_active}, Has Password: {user.has_usable_password()}')
"
```

#### Test Password Reset Flow
```bash
# Test complete password reset process
python manage.py shell -c "
from django.test import Client
client = Client()

# Request password reset
response = client.post('/accounts/password/reset/', {'email': 'joe@coophive.network'})
print(f'Reset request: {response.status_code}')

# Check console for verification code
print('Check server console for verification code')
"
```

## Best Practices

### Development
1. **Use `.env` file** for local email credentials
2. **Test email sending** before deploying
3. **Verify super admin access** after setup
4. **Keep credentials secure** - never commit to git

### Production
1. **Environment variables** for initial deployment
2. **Database storage** for runtime flexibility
3. **Email monitoring** - track sending success/failures
4. **Backup credentials** - store securely offline

### Maintenance
1. **Regular testing** - verify email functionality
2. **Credential rotation** - update passwords periodically
3. **Monitor logs** - watch for authentication errors
4. **Update documentation** - keep setup guides current

## Migration from Environment-Only

If you currently use only environment variables:

1. **Current setup continues working** - no breaking changes
2. **Optional migration** - move to database when convenient
3. **Hybrid approach** - mix database and environment as needed
4. **Gradual transition** - migrate settings one by one

### Migration Steps
```bash
# 1. Check current configuration
python manage.py init_email --check

# 2. Move credentials to database
python manage.py init_email --set-user "$EMAIL_HOST_USER"
python manage.py init_email --set-password "$EMAIL_HOST_PASSWORD"

# 3. Verify new configuration
python manage.py init_email --check

# 4. Test email sending
python manage.py init_email --test "your-email@example.com"

# 5. Optional: Remove from .env file
# (system will now use database values)
```

This guide ensures super admins can access the system immediately while maintaining flexibility and security in email configuration.
