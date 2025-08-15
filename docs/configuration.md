# Configuration Guide

## Environment Variables

### Required Environment Variables
```bash
# Django Core
SECRET_KEY=your-secret-key
DEBUG=True|False
ALLOWED_HOSTS=host1,host2,host3
DATABASE_URL=postgresql://user:pass@host:port/dbname

# Email Configuration (Required for super admin password reset)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=465
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-gmail-app-password
DEFAULT_FROM_EMAIL=noreply@coophive.network

# Note: Gmail requires app passwords, not regular passwords
# Port 465 uses SSL, port 587 uses TLS

# Domain Restriction
DOMAIN_RESTRICTION_ENABLED=True
ALLOWED_DOMAIN=coophive.network

# Google OAuth (database-first via app_settings) - WORKING!
GOOGLE_OAUTH_CLIENT_ID=your-google-client-id
GOOGLE_OAUTH_CLIENT_SECRET=your-google-client-secret
# Note: OAuth credentials are stored in database via app_settings
# Environment variables serve as fallback during initial setup

# Social Media API Keys
LINKEDIN_CLIENT_ID=your-client-id
LINKEDIN_CLIENT_SECRET=your-client-secret
TWITTER_API_KEY=your-api-key
TWITTER_API_SECRET=your-api-secret
FARCASTER_KEY=your-farcaster-key
BLUESKY_HANDLE=your-handle
BLUESKY_APP_PASSWORD=your-app-password
```

## Django Settings

### Base Settings (settings.py)

#### Application Definition
```python
INSTALLED_APPS = [
    # Django apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    
    # Third party apps
    'rest_framework',
    'debug_toolbar',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    
    # Local apps
    'user_account_manager.apps.UserAccountManagerConfig',
    'app_settings.apps.AppSettingsConfig',
    'core.apps.CoreConfig',
    'linkedin.apps.LinkedinConfig',
    'twitter.apps.TwitterConfig',
    'farcaster.apps.FarcasterConfig',
    'bluesky.apps.BlueskyConfig',
]
```

#### Middleware Configuration
```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]
```

#### Template Configuration
```python
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
```

#### Database Configuration
```python
DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///db.sqlite3',
        conn_max_age=600
    )
}
```

#### Auth Configuration
```python
# Custom authentication backends
AUTHENTICATION_BACKENDS = [
    'user_account_manager.backends.EmailOrUsernameModelBackend',  # Custom backend for email/username login
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# Django-allauth settings
SITE_ID = 1
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# Use custom adapter for Google OAuth with domain restrictions
SOCIALACCOUNT_ADAPTER = 'user_account_manager.adapters.CustomSocialAccountAdapter'

# Allauth social account settings (TaskForge-style)
SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_EMAIL_REQUIRED = False  # Don't require email confirmation
SOCIALACCOUNT_EMAIL_VERIFICATION = "none"  # Skip ALL email verification
SOCIALACCOUNT_LOGIN_ON_GET = True  # Direct login without confirmation page
SOCIALACCOUNT_SIGNUP_FORM_CLASS = None  # No signup form
SOCIALACCOUNT_FORMS = {}  # No custom forms

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        # No APP config - allauth will use SocialApp from database (WORKING!)
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        },
        'OAUTH_PKCE_ENABLED': False,  # Fixed token issues - WORKING!
        'FETCH_USERINFO': True,
        'VERIFIED_EMAIL': True,  # Trust Google's email verification
    }
}
```

#### REST Framework Settings
```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}
```

#### Cache Configuration
```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
    }
}
```

#### Email Configuration (Database-First with Environment Fallback) - ✅ WORKING!
```python
# Custom email backend that loads settings dynamically
EMAIL_BACKEND = 'user_account_manager.email_backend.DatabaseFirstEmailBackend'

# Fallback settings when database is unavailable
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 465))  # Gmail SSL port
EMAIL_USE_SSL = os.getenv('EMAIL_USE_SSL', 'True').lower() == 'true'  # SSL for Gmail
EMAIL_USE_TLS = False  # Don't use TLS when using SSL
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@coophive.network')
```

#### Email Backend Features - ✅ FULLY FUNCTIONAL
- **Database-first**: Email settings loaded from `AppSetting` model via `SettingsManager`
- **Environment fallback**: Uses `.env` file when database unavailable
- **Gmail SSL support**: Automatically uses SSL for port 465, prevents TLS/SSL conflicts
- **Runtime configuration**: Settings loaded dynamically, not at startup
- **Fixed timeout issues**: Proper SSL configuration resolves SMTP timeout errors
- **Password reset working**: Super admins can reset passwords via email at `/accounts/password/reset/`

## Production Settings

### Security Settings
```python
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
```

### Static/Media Files
```python
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

## Development Tools

### Django Debug Toolbar
```python
if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
    INTERNAL_IPS = ['127.0.0.1']
```

### Logging Configuration
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs/debug.log',
        },
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```
