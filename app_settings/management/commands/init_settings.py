from django.core.management.base import BaseCommand
from app_settings.models import AppSetting

class Command(BaseCommand):
    help = 'Initialize application settings with default values'

    def handle(self, *args, **options):
        settings_to_create = [
            # Google OAuth Settings
            {
                'key': 'GOOGLE_OAUTH_CLIENT_ID',
                'value': '',
                'description': 'Google OAuth Client ID for authentication'
            },
            {
                'key': 'GOOGLE_OAUTH_CLIENT_SECRET',
                'value': '',
                'description': 'Google OAuth Client Secret for authentication'
            },
            
            # Email Settings - Database-first with environment fallback
            {
                'key': 'EMAIL_HOST',
                'value': 'smtp.gmail.com',
                'description': 'SMTP server hostname (default: Gmail)'
            },
            {
                'key': 'EMAIL_PORT',
                'value': '587',
                'description': 'SMTP server port (default: 587 for TLS)'
            },
            {
                'key': 'EMAIL_USE_TLS',
                'value': 'True',
                'description': 'Use TLS encryption for email (True/False)'
            },
            {
                'key': 'EMAIL_HOST_USER',
                'value': 'joe@coophive.network',
                'description': 'Email username - leave empty to use environment variable'
            },
            {
                'key': 'EMAIL_HOST_PASSWORD',
                'value': 'tgws eabi xakt mmks',
                'description': 'Email password - leave empty to use environment variable'
            },
            {
                'key': 'DEFAULT_FROM_EMAIL',
                'value': 'noreply@coophive.network',
                'description': 'Default sender email address'
            },
            
            # Domain Restriction Settings
            {
                'key': 'DOMAIN_RESTRICTION_ENABLED',
                'value': 'True',
                'description': 'Enable domain restrictions for user registration'
            },
            {
                'key': 'ALLOWED_DOMAIN',
                'value': 'coophive.network',
                'description': 'Allowed email domain for registration'
            },
            {
                'key': 'GOOGLE_VERIFICATION_ENABLED',
                'value': 'True',
                'description': 'Enable Google OAuth domain verification'
            },
        ]

        for setting in settings_to_create:
            _, created = AppSetting.objects.get_or_create(
                key=setting['key'],
                defaults={
                    'value': setting['value'],
                    'description': setting['description']
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created setting: {setting["key"]}'))
            else:
                self.stdout.write(f'Setting already exists: {setting["key"]}')
