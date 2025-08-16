"""
Django settings for coophive project.

100% Database-First Settings Configuration
- All settings except super admin emails use database-first, environment fallback approach
- NO hardcoded defaults for security-critical settings
- Fail securely if required settings are missing
"""

from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import database-first settings helper
from app_settings.django_settings import get_credential_setting, get_secret_setting, get_bool_setting

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# =============================================================================
# CRITICAL SECURITY SETTINGS - Database First, Environment Fallback
# =============================================================================

# SECRET_KEY: MUST be configured via database or environment
try:
    SECRET_KEY = get_secret_setting('SECRET_KEY')
except Exception:
    # Fallback during initial setup/migrations when database might not exist
    SECRET_KEY = os.getenv('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError(
            "SECRET_KEY must be set via environment variable or database. "
            "Run: python manage.py init_settings_new"
        )

# DEBUG: Database first, environment fallback, secure default
try:
    DEBUG = get_bool_setting('DEBUG')
except Exception:
    # Fallback during initial setup
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# Railway environment detection and configuration
RAILWAY_STATIC_URL = os.getenv('RAILWAY_STATIC_URL', '')
RAILWAY_PUBLIC_DOMAIN = os.getenv('RAILWAY_PUBLIC_DOMAIN', '')

# Build allowed hosts for Railway
RAILWAY_HOSTS = []
if RAILWAY_STATIC_URL:
    # Extract hostname from RAILWAY_STATIC_URL
    hostname = RAILWAY_STATIC_URL.replace('https://', '').replace('http://', '').rstrip('/')
    RAILWAY_HOSTS.append(hostname)

if RAILWAY_PUBLIC_DOMAIN:
    RAILWAY_HOSTS.append(RAILWAY_PUBLIC_DOMAIN)

# Always allow Railway.app domains and localhost
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '*.railway.app',
    'coophivesocialmediamanager-production.up.railway.app',  # Explicit Railway domain
] + RAILWAY_HOSTS

# CSRF settings - trust Railway domains
CSRF_TRUSTED_ORIGINS = [
    'https://*.railway.app',
    'https://coophivesocialmediamanager-production.up.railway.app',
]
if RAILWAY_STATIC_URL:
    CSRF_TRUSTED_ORIGINS.append(RAILWAY_STATIC_URL)

# Security settings
if not DEBUG:
    # Railway handles SSL termination - don't redirect at Django level
    SECURE_SSL_REDIRECT = False
    # But still secure cookies since Railway forwards with HTTPS headers
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    
    # Railway proxy headers for security
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',  # Required for django-allauth
    
    # Third party apps
    'rest_framework',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    
    # Local apps
    'user_account_manager.apps.UserAccountManagerConfig',
    'app_settings.apps.AppSettingsConfig',  # Database settings management
    'core.apps.CoreConfig',
    'linkedin.apps.LinkedinConfig',
    'twitter.apps.TwitterConfig',
    'farcaster.apps.FarcasterConfig',
    'bluesky.apps.BlueskyConfig',
]

# Add debug toolbar only if DEBUG is True and package is available
if DEBUG:
    try:
        import debug_toolbar
        INSTALLED_APPS.append('debug_toolbar')
    except ImportError:
        pass

# Email configuration - will be overridden below with database-first backend

# Authentication settings
LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# Domain restriction - DISABLED for Railway deployment to prevent redirect loops
COOPHIVE_DOMAIN_RESTRICTION = {
    'ENABLED': False,  # Temporarily disabled for Railway deployment
    'ALLOWED_DOMAIN': 'coophive.network',
}

# Django Debug Toolbar
if DEBUG:
    INTERNAL_IPS = ['127.0.0.1']

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Static files in production
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

# Add debug toolbar middleware only if DEBUG is True and package is available
if DEBUG:
    try:
        import debug_toolbar
        MIDDLEWARE.append('debug_toolbar.middleware.DebugToolbarMiddleware')
        INTERNAL_IPS = ['127.0.0.1']
    except ImportError:
        pass

ROOT_URLCONF = 'coophive.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'coophive.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# Whitenoise configuration
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Create required directories
for directory in [STATIC_ROOT, *STATICFILES_DIRS]:
    os.makedirs(directory, exist_ok=True)

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Authentication Settings
AUTHENTICATION_BACKENDS = [
    # Custom backend for email/username login
    'user_account_manager.backends.EmailOrUsernameModelBackend',
    # Django default (for admin)
    'django.contrib.auth.backends.ModelBackend',
    # Allauth backend (for social login)
    'allauth.account.auth_backends.AuthenticationBackend',
]

# django-allauth settings
SITE_ID = 1
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# Use custom adapter for Google OAuth with domain restrictions
SOCIALACCOUNT_ADAPTER = 'user_account_manager.adapters.CustomSocialAccountAdapter'

# Allauth social account settings
SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_EMAIL_REQUIRED = False  # Don't require email confirmation
SOCIALACCOUNT_EMAIL_VERIFICATION = "none"  # Skip ALL email verification
SOCIALACCOUNT_LOGIN_ON_GET = True  # Direct login without confirmation page
SOCIALACCOUNT_SIGNUP_FORM_CLASS = None  # No signup form
SOCIALACCOUNT_FORMS = {}  # No custom forms

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        # No APP config - allauth will use SocialApp from database
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        },
        'OAUTH_PKCE_ENABLED': False,  # Disable PKCE to fix token issues
        'FETCH_USERINFO': True,
        'VERIFIED_EMAIL': True,  # Trust Google's email verification
    }
}

# =============================================================================
# EMAIL SETTINGS - Database First, Environment Fallback
# =============================================================================

# Use custom backend that loads settings dynamically from database
EMAIL_BACKEND = 'user_account_manager.email_backend.DatabaseFirstEmailBackend'

# Database-first email settings with environment fallback
try:
    EMAIL_HOST = get_credential_setting('EMAIL_HOST', required=True)
    EMAIL_PORT = get_credential_setting('EMAIL_PORT', value_type=int, required=True)
    EMAIL_USE_SSL = get_credential_setting('EMAIL_USE_SSL', value_type=bool, required=True)
    EMAIL_USE_TLS = get_credential_setting('EMAIL_USE_TLS', value_type=bool, required=True)
    EMAIL_HOST_USER = get_credential_setting('EMAIL_HOST_USER', required=True)
    EMAIL_HOST_PASSWORD = get_credential_setting('EMAIL_HOST_PASSWORD', required=True)
    DEFAULT_FROM_EMAIL = get_credential_setting('DEFAULT_FROM_EMAIL', required=True)
except Exception:
    # Fallback during initial setup - but log warning
    EMAIL_HOST = os.getenv('EMAIL_HOST', '')
    EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587')) if os.getenv('EMAIL_PORT') else 587
    EMAIL_USE_SSL = os.getenv('EMAIL_USE_SSL', 'False').lower() == 'true'
    EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True').lower() == 'true'
    EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
    EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
    DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', '')

# =============================================================================
# DOMAIN RESTRICTION SETTINGS - Database First, Environment Fallback
# =============================================================================

try:
    COOPHIVE_DOMAIN_RESTRICTION = {
        'ENABLED': get_credential_setting('DOMAIN_RESTRICTION_ENABLED', value_type=bool, required=True),
        'GOOGLE_VERIFICATION': get_credential_setting('GOOGLE_VERIFICATION_ENABLED', value_type=bool, required=True),
        'ALLOWED_DOMAIN': get_credential_setting('ALLOWED_DOMAIN', required=True),
        'SECURITY_ADMIN_EMAILS': get_credential_setting('SUPER_ADMIN_EMAILS'),  # Hardcoded allowed
        'ADMIN_BYPASS': False,  # Always false for security
        'LOG_USER_AGENTS': True,  # Always true for security
    }
except Exception:
    # Fallback during initial setup
    COOPHIVE_DOMAIN_RESTRICTION = {
        'ENABLED': os.getenv('DOMAIN_RESTRICTION_ENABLED', 'True').lower() == 'true',
        'GOOGLE_VERIFICATION': os.getenv('GOOGLE_VERIFICATION_ENABLED', 'True').lower() == 'true',
        'ALLOWED_DOMAIN': os.getenv('ALLOWED_DOMAIN', 'coophive.network'),
        'SECURITY_ADMIN_EMAILS': ['joe@coophive.network', 'levi@coophive.network'],  # Hardcoded
        'ADMIN_BYPASS': False,
        'LOG_USER_AGENTS': True,
    }

# Logging Configuration
# Create logs directory if it doesn't exist and we're not in a managed environment
if not (os.getenv('CI') or os.getenv('RAILWAY_ENVIRONMENT_NAME')):
    logs_dir = os.path.join(BASE_DIR, 'logs')
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)

# Determine if we're in a managed environment (CI or Railway)
IS_MANAGED_ENV = bool(os.getenv('CI') or os.getenv('RAILWAY_ENVIRONMENT_NAME'))

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.StreamHandler' if IS_MANAGED_ENV else 'logging.handlers.RotatingFileHandler',
            'formatter': 'simple' if IS_MANAGED_ENV else 'verbose',
            **({"filename": os.path.join(BASE_DIR, 'logs/debug.log'),
                "maxBytes": 1024 * 1024 * 5,  # 5 MB
                "backupCount": 5} if not IS_MANAGED_ENV else {}),
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'] if IS_MANAGED_ENV else ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'core': {
            'handlers': ['console'] if IS_MANAGED_ENV else ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'social': {
            'handlers': ['console'] if IS_MANAGED_ENV else ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
