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
│   ├── apps.py                  # App configuration
│   ├── forms.py                 # Authentication forms
│   ├── models.py               # User model customization
│   ├── urls.py                 # Authentication URLs
│   ├── views.py                # Authentication views
│   ├── adapters.py             # Social auth adapters
│   ├── utils.py                # Authentication utilities
│   ├── migrations/             # Database migrations
│   ├── templates/
│   │   └── user_account_manager/
│   │       ├── login.html
│   │       ├── register.html
│   │       └── profile.html
│   └── management/
│       └── commands/
│           └── setup_google_oauth.py
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
│   ├── _base.html              # Base template
│   ├── _nav.html               # Navigation component
│   ├── _footer.html            # Footer component
│   └── components/             # Reusable components
│
├── static/                      # Static files
│   ├── css/
│   │   └── styles.css
│   ├── js/
│   │   └── main.js
│   └── img/
│
├── docs/                        # Project documentation
│   ├── deployment.md
│   ├── development.md
│   └── testing.md
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
    
    # Authentication URLs
    path('accounts/', include('allauth.urls')),
    path('user_account_manager/', include('user_account_manager.urls')),
    
    # Platform URLs
    path('linkedin/', include('linkedin.urls')),
    path('twitter/', include('twitter.urls')),
    path('farcaster/', include('farcaster.urls')),
    path('bluesky/', include('bluesky.urls')),
    
    # Core URLs
    path('', include('core.urls')),
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

### URLs Structure

Core authentication URLs (namespace: 'user_account_manager'):
- `/user_account_manager/login/` - Login page (`user_account_manager:login`)
- `/user_account_manager/register/` - Registration page (`user_account_manager:register`)
- `/user_account_manager/profile/` - User profile (`user_account_manager:profile`)
- `/user_account_manager/verify/` - Email verification (`user_account_manager:verify`)
- `/user_account_manager/verify-otp/` - OTP verification (`user_account_manager:verify_otp`)
- `/user_account_manager/reset/` - Password reset (`user_account_manager:reset`)

Social Authentication URLs (handled by django-allauth):
- `/accounts/google/login/` - Google OAuth login
- `/accounts/google/login/callback/` - Google OAuth callback

### Google OAuth Setup

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

# Initialize settings database
python manage.py init_settings

# Create superuser
python manage.py createsuperuser
```

5. Set up development tools:
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
