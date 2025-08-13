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
            {
                'key': 'GOOGLE_OAUTH_CLIENT_SECRET',
                'value': '',
                'description': 'Google OAuth Client Secret for authentication'
            },
            {
                'key': 'EMAIL_HOST_USER',
                'value': '',
                'description': 'Email host username for sending emails'
            },
            {
                'key': 'EMAIL_HOST_PASSWORD',
                'value': '',
                'description': 'Email host password for sending emails'
            },
            {
                'key': 'DEFAULT_FROM_EMAIL',
                'value': '',
                'description': 'Default sender email address'
            }
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
