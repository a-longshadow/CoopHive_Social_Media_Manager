from django.core.management.base import BaseCommand
from django.db import transaction
from app_settings.models import AppSetting

class Command(BaseCommand):
    help = 'Initialize application settings with default values'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force update existing settings',
        )

    def handle(self, *args, **options):
        # SECURITY: NO hardcoded values - all settings must be configured via environment or admin
        settings_to_create = [
            # Django Core Settings - MUST be configured
            {
                'key': 'SECRET_KEY',
                'value': '',  # NO DEFAULT - must be set via environment or admin
                'description': 'Django secret key for cryptographic signing - CRITICAL for security. MUST be set via environment variable or admin interface.'
            },
            {
                'key': 'DEBUG',
                'value': '',  # NO DEFAULT - must be set via environment or admin
                'description': 'Django debug mode (True/False) - should be False in production. MUST be set via environment variable or admin interface.'
            },
            
            # Google OAuth Settings - MUST be configured for OAuth to work
            {
                'key': 'GOOGLE_OAUTH_CLIENT_ID',
                'value': '',  # NO DEFAULT - must be configured
                'description': 'Google OAuth Client ID for authentication. MUST be configured for Google OAuth to work.'
            },
            {
                'key': 'GOOGLE_OAUTH_CLIENT_SECRET',
                'value': '',  # NO DEFAULT - must be configured
                'description': 'Google OAuth Client Secret for authentication. MUST be configured for Google OAuth to work.'
            },
            
            # Email Settings - MUST be configured for email to work
            {
                'key': 'EMAIL_HOST',
                'value': '',  # NO DEFAULT - must be configured
                'description': 'SMTP server hostname (e.g., smtp.gmail.com). MUST be configured for email to work.'
            },
            {
                'key': 'EMAIL_PORT',
                'value': '',  # NO DEFAULT - must be configured
                'description': 'SMTP server port (e.g., 587 for TLS, 465 for SSL). MUST be configured for email to work.'
            },
            {
                'key': 'EMAIL_USE_TLS',
                'value': '',  # NO DEFAULT - must be configured
                'description': 'Use TLS encryption for email (True/False). MUST be configured for email to work.'
            },
            {
                'key': 'EMAIL_HOST_USER',
                'value': '',  # NO DEFAULT - must be configured
                'description': 'Email username/address. MUST be configured for email to work.'
            },
            {
                'key': 'EMAIL_HOST_PASSWORD',
                'value': '',  # NO DEFAULT - must be configured
                'description': 'Email password or app password. MUST be configured for email to work.'
            },
            {
                'key': 'DEFAULT_FROM_EMAIL',
                'value': '',  # NO DEFAULT - must be configured
                'description': 'Default sender email address. MUST be configured for email to work.'
            },
            
            # Domain Restriction Settings - MUST be configured
            {
                'key': 'DOMAIN_RESTRICTION_ENABLED',
                'value': '',  # NO DEFAULT - must be configured
                'description': 'Enable domain restrictions for user registration (True/False). MUST be configured.'
            },
            {
                'key': 'ALLOWED_DOMAIN',
                'value': '',  # NO DEFAULT - must be configured
                'description': 'Allowed email domain for registration (e.g., coophive.network). MUST be configured.'
            },
            {
                'key': 'GOOGLE_VERIFICATION_ENABLED',
                'value': '',  # NO DEFAULT - must be configured
                'description': 'Enable Google OAuth domain verification (True/False). MUST be configured.'
            },
            
            # Super Admin Settings - Only hardcoded values allowed
            {
                'key': 'SUPER_ADMIN_EMAILS',
                'value': 'joe@coophive.network,levi@coophive.network',  # ONLY hardcoded values allowed per requirements
                'description': 'Comma-separated list of super admin email addresses. These are the only hardcoded values in the system.'
            },
        ]

        try:
            with transaction.atomic():
                created_count = 0
                existing_count = 0
                
                for setting in settings_to_create:
                    _, created = AppSetting.objects.get_or_create(
                        key=setting['key'],
                        defaults={
                            'value': setting['value'],
                            'description': setting['description']
                        }
                    )
                    if created:
                        created_count += 1
                        self.stdout.write(self.style.SUCCESS(f'✓ Created setting: {setting["key"]}'))
                    else:
                        existing_count += 1
                        self.stdout.write(f'→ Setting already exists: {setting["key"]}')
                
                self.stdout.write(
                    self.style.SUCCESS(f'\n✅ Settings initialization complete! Created: {created_count}, Existing: {existing_count}')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error initializing settings: {str(e)}')
            )
            # Don't raise in production to avoid deployment failures
            if options.get('verbosity', 1) > 1:
                raise
