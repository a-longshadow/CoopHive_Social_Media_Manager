# Development Guide

## Project Structure

The project follows a modular architecture with multiple Django apps. Here's the complete project skeleton:

```
CoopHive_Social_Media_Manager/
│
├── coophive/                      # Main project configuration
│   ├── __init__.py
│   ├── settings.py               # Core settings and app configurations
│   ├── urls.py                  # Root URL configuration
│   └── wsgi.py                  # WSGI application entry point
│
├── app_settings/                  # Database-driven settings management
│   ├── __init__.py
│   ├── admin.py                 # Admin interface for settings
│   ├── apps.py                  # App configuration
│   ├── models.py               # AppSetting model definition
│   ├── manager.py              # Settings manager implementation
│   ├── migrations/             # Database migrations
│   └── management/
│       └── commands/
│           └── init_settings.py # Initialize default settings
│
├── user_account_manager/          # User authentication and management
│   ├── __init__.py
│   ├── admin.py                 # User admin customization
│   ├── apps.py                  # App configuration with auto super admin creation
│   ├── forms.py                 # Authentication forms (TaskForge-style)
│   ├── models.py               # User model and verification codes
│   ├── urls.py                 # Authentication URLs (accounts namespace)
│   ├── views.py                # Authentication views with Google OAuth
│   ├── adapters.py             # Social auth adapters with domain restrictions
│   ├── backends.py             # Custom auth backends (email/username login)
│   ├── utils.py                # Authentication utilities (DB-first settings)
│   ├── email_backend.py        # Custom database-first email backend
│   ├── migrations/             # Database migrations
│   ├── templatetags/           # Custom template tags
│   │   ├── __init__.py
│   │   └── form_tags.py        # Form styling template filters
│   ├── templates/
│   │   └── accounts/           # Modern TaskForge-styled templates
│   │       ├── login.html      # Modern login with Google OAuth
│   │       ├── register.html   # Modern registration with Google OAuth
│   │       ├── verify.html     # Email verification
│   │       ├── google_verify.html # Google OAuth verification
│   │       ├── reset_request.html # Password reset request
│   │       └── reset_verify.html  # Password reset verification
│   ├── tests/                  # Comprehensive test suite
│   │   ├── __init__.py
│   │   └── test_authentication.py # 24 authentication tests
│   └── management/
│       └── commands/
│           ├── setup_google_oauth.py # Google OAuth setup helper
│           ├── create_super_admins.py # Auto-create hardcoded super admins
│           └── init_email.py    # Email configuration management
│
├── core/                         # Core functionality
│   ├── __init__.py
│   ├── apps.py
│   ├── urls.py                  # Main site URLs
│   ├── views.py                 # Core views (homepage, etc)
│   └── templates/
│       └── core/
│           └── home.html
│
├── Platform Apps/                # Social media platform integrations
│   │
│   ├── linkedin/                # LinkedIn integration
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── models.py           # Post and media models
│   │   ├── urls.py             # LinkedIn-specific URLs
│   │   ├── views.py            # Platform views
│   │   ├── api.py              # LinkedIn API integration
│   │   └── templates/
│   │       └── linkedin/
│   │           ├── dashboard.html
│   │           └── post_form.html
│   │
│   ├── twitter/                 # Twitter integration
│   │   ├── [similar structure to linkedin]
│   │
│   ├── farcaster/              # Farcaster integration
│   │   ├── [similar structure to linkedin]
│   │
│   └── bluesky/                # Bluesky integration
│       └── [similar structure to linkedin]
│
├── templates/                    # Global templates
│   ├── base.html               # Modern base template with TaskForge styling
│   ├── _nav.html               # Navigation component (integrated into base.html)
│   ├── 404.html                # Error page
│   └── home.html               # Homepage template
│
├── static/                      # Static files
│   ├── coophive_logo.svg       # Custom CoopHive logo
│   ├── css/
│   │   └── styles.css
│   ├── js/
│   │   └── main.js
│   └── img/
│
├── docs/                        # Project documentation
│   ├── api.md                  # API documentation
│   ├── configuration.md        # Configuration guide
│   ├── deployment.md          # Deployment guide
│   ├── development.md         # Development guide
│   ├── forms.md               # Forms documentation
│   ├── models.md              # Database models
│   ├── testing.md             # Testing guide
│   ├── ui_modernization.md    # UI modernization details
│   └── super_admin_setup.md   # Super admin & email setup
│
├── .github/                     # GitHub configuration
│   └── workflows/
│       ├── tests.yml           # CI pipeline
│       └── deploy.yml          # CD pipeline
│
├── manage.py                    # Django management script
├── requirements.txt             # Python dependencies
├── pytest.ini                  # Test configuration
├── .env.example                # Environment variables template
├── .gitignore                  # Git ignore rules
├── Procfile                    # Heroku deployment
├── runtime.txt                 # Python runtime spec
└── .pre-commit-config.yaml     # Pre-commit hooks config
```
```

## Core Configuration Files

### Project Settings (`coophive/settings.py`)
Key configurations include:
```python
INSTALLED_APPS = [
    # Django apps
    'django.contrib.admin',
    'django.contrib.auth',
    ...
    
    # Third-party apps
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

# Authentication settings
LOGIN_URL = 'user_account_manager:login'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# Domain restriction
COOPHIVE_DOMAIN_RESTRICTION = {
    'ENABLED': True,
    'ALLOWED_DOMAIN': 'coophive.network',
}
```

### URL Configuration (`coophive/urls.py`)
```python
urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Custom authentication URLs (prioritized over allauth)
    path('accounts/', include('user_account_manager.urls', namespace='accounts')),
    
    # Allauth URLs (for Google OAuth and other social auth)
    path('accounts/', include('allauth.urls')),
    
    # Homepage and core functionality
    path('', include('core.urls')),
    
    # Platform-specific URLs
    path('twitter/', include('twitter.urls')),
    path('linkedin/', include('linkedin.urls')),
    path('farcaster/', include('farcaster.urls')),
    path('bluesky/', include('bluesky.urls')),
]
```

## Core Components

### 1. Settings Management (`app_settings`)
Database-driven settings management system that stores all configurations in the database:

#### Key Files

`models.py`:
```python
class AppSetting(models.Model):
    key = models.CharField(max_length=100, unique=True, db_index=True)
    value = models.TextField(blank=True)
    description = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

`manager.py`:
```python
class SettingsManager:
    def get(self, key: str, default: Any = None) -> Any:
        """Get a setting value."""
        try:
            setting = AppSetting.objects.get(key=key)
            return self._deserialize_value(setting.value)
        except AppSetting.DoesNotExist:
            return default

    def set(self, key: str, value: Any, description: str = "") -> None:
        """Set a setting value."""
        serialized_value = self._serialize_value(value)
        AppSetting.objects.update_or_create(
            key=key,
            defaults={"value": serialized_value, "description": description}
        )
```

`management/commands/init_settings.py`:
```python
class Command(BaseCommand):
    help = 'Initialize application settings'

    def handle(self, *args, **options):
        settings_to_create = [
            {
                'key': 'GOOGLE_OAUTH_CLIENT_ID',
                'value': '',
                'description': 'Google OAuth Client ID'
            },
            {
                'key': 'GOOGLE_OAUTH_CLIENT_SECRET',
                'value': '',
                'description': 'Google OAuth Client Secret'
            }
        ]
        # Initialize settings...
```

#### Usage:
```python
from app_settings.settings import SettingsManager

# Get a setting
oauth_id = SettingsManager.get('GOOGLE_OAUTH_CLIENT_ID')

# Set a setting
SettingsManager.set('GOOGLE_OAUTH_CLIENT_ID', 'new_value', 'OAuth client ID for Google')
```

## Authentication

Authentication is handled by the `user_account_manager` app, which integrates both custom authentication and social authentication via `django-allauth`.

### Super Admin Users - ✅ FULLY WORKING!
The system automatically creates hardcoded super admin users:
- **`joe@coophive.network`** - Primary super admin  
- **`levi@coophive.network`** - Secondary super admin

**Access Methods (Both Working):**
1. **Google OAuth**: `/accounts/login/` → "Continue with Google" ✅
2. **Password Reset**: `/accounts/password/reset/` → Email verification ✅

**Recent Fixes:**
- ✅ **Email timeout fixed**: SSL port 465 configuration working
- ✅ **Database settings**: SettingsManager properly reads from database
- ✅ **SMTP working**: Gmail app password authentication successful
- ✅ **Password reset flow**: Emails sent to Gmail inbox (not console)

For complete setup instructions, see [`docs/super_admin_setup.md`](super_admin_setup.md).

### URLs Structure

Core authentication URLs (namespace: 'accounts'):
- `/accounts/login/` - Modern login page with Google OAuth (`accounts:login`)
- `/accounts/register/` - Modern registration page with Google OAuth (`accounts:register`)
- `/accounts/verify/` - Email verification (`accounts:verify`)
- `/accounts/google/verify/` - Google OAuth verification (`accounts:google-verify`)
- `/accounts/reset/` - Password reset request (`accounts:reset`)
- `/accounts/password/verify/` - Password reset verification (`accounts:reset-verify`)
- `/accounts/logout/` - User logout (`accounts:logout`)
- `/accounts/domain-breach/` - Domain restriction breach handler (`accounts:domain-breach`)

Social Authentication URLs (handled by django-allauth):
- `/accounts/google/login/` - Google OAuth login
- `/accounts/google/login/callback/` - Google OAuth callback

### Google OAuth Setup (WORKING!)

✅ **Google OAuth is fully functional** with proper TaskForge-style implementation.

To set up Google OAuth:

1. Run the management command:
```bash
python manage.py setup_google_oauth
```

2. Follow the prompts to:
   - Create a Google Cloud Project
   - Configure OAuth consent screen
   - Create OAuth 2.0 credentials
   - Add authorized redirect URIs:
     - http://localhost:8000/accounts/google/login/callback/
     - http://127.0.0.1:8000/accounts/google/login/callback/
     - Your production domain callback URL

**OAuth Features:**
- ✅ Working "Continue with Google" buttons
- ✅ Proper 302 redirect flow (no more 200 error pages)
- ✅ Domain restriction handling with beautiful error pages
- ✅ Super admin access via Google OAuth
- ✅ Database-first credential storage with environment fallback

## Development Setup

1. Create and activate virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Initialize database:
```bash
# Generate migrations for user_account_manager
python manage.py makemigrations user_account_manager

# Run all migrations
python manage.py migrate

# Initialize settings database (includes email credentials)
python manage.py init_settings

# Super admins are created automatically (joe@coophive.network, levi@coophive.network)
# No manual superuser creation needed!
```

5. Configure email for super admin access:
```bash
# Check current email configuration
python manage.py init_email --check

# Set email credentials in database (optional - can use .env file)
python manage.py init_email --set-user "your-email@gmail.com"
python manage.py init_email --set-password "your-gmail-app-password"

# Test email sending
python manage.py init_email --test "your-email@gmail.com"
```

6. Set up development tools:
```bash
# Install pre-commit hooks
pre-commit install

# Verify installation
pre-commit run --all-files
```

## Testing

### Test Configuration
Tests are configured using pytest (see `pytest.ini`):
```ini
[pytest]
DJANGO_SETTINGS_MODULE = coophive.settings
python_files = tests.py test_*.py *_tests.py
filterwarnings =
    ignore::DeprecationWarning
    ignore::UserWarning
```

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov

# Run specific app tests
pytest linkedin/
pytest twitter/
```

## Template Structure

### Global Templates (`/templates`)
- Base templates and layouts
- Shared components
- Navigation and footer

### App-Specific Templates
Each app has its own templates directory:
```
app_name/
└── templates/
    └── app_name/
        ├── dashboard.html
        ├── post_list.html
        └── components/
```

## Static Files

### Organization
```
static/
├── css/
├── js/
├── img/
└── vendors/
```

### Development vs Production
- Development: Served by Django's development server
- Production: Collected to STATIC_ROOT and served by nginx/CDN

## Logging

Logging is configured to write to `logs/` directory:
- `debug.log` - All DEBUG and above messages
- `error.log` - ERROR and above messages
- Console output in development

## CI/CD Pipeline

### GitHub Actions (`.github/`)
- Runs tests on pull requests
- Checks code style (flake8, black)
- Runs security checks
- Automated deployments

### Deployment Options
1. Railway (Primary)
   - See `docs/deployment.md` for setup
   - Automated deployments from main branch
   - PostgreSQL integration

2. Heroku (Alternative)
   - Uses `Procfile` and `runtime.txt`
   - Similar setup to Railway
   - Supports review apps

## Development Best Practices

### 1. Code Style
- Follow PEP 8 guidelines
- Use Black for formatting
- Run pre-commit hooks before committing
- Use type hints where possible

### 2. Git Workflow
- Create feature branches from main
- Use meaningful commit messages
- Submit pull requests for review
- Keep branches up to date with main

### 3. Testing Guidelines
- Write tests for new features
- Mock external services
- Test error cases
- Maintain test coverage above 80%

### 4. Documentation
- Update docs with code changes
- Document API endpoints
- Keep README.md current
- Add comments for complex logic

### 5. Security
- Never commit sensitive data
- Use app_settings for configurations
- Validate user input
- Follow security best practices

## Troubleshooting

### Common Issues
1. Database Migrations
   ```bash
   python manage.py migrate --fake-initial
   ```

2. Static Files
   ```bash
   python manage.py collectstatic --noinput
   ```

3. Settings Management
   ```bash
   python manage.py init_settings --force
   ```
# Generate migrations for user_account_manager
python manage.py makemigrations user_account_manager

# Run all migrations
python manage.py migrate

# Set up initial site configuration (required for OAuth)
python manage.py setup_google_oauth
```

5. Create superuser:
```bash
python manage.py createsuperuser
```

6. Run development server:
```bash
python manage.py runserver
```

## Testing

Run tests with:
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test user_account_manager
```

## Code Style

We follow PEP 8 guidelines for Python code. Use Black for code formatting:
```bash
black .
```
