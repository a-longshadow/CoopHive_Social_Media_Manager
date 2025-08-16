from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth import get_user_model
from app_settings.models import AppSetting

User = get_user_model()

class Command(BaseCommand):
    help = 'Initialize application settings with database-first approach (NO hardcoded defaults)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force update existing settings',
        )
        parser.add_argument(
            '--create-super-admins',
            action='store_true',
            help='Create super admin accounts from hardcoded emails',
        )

    def handle(self, *args, **options):
        """
        Initialize 100% database-first settings.
        NO hardcoded defaults except super admin emails.
        """
        
        # Critical security settings that MUST be configured
        critical_settings = [
            {
                'key': 'SECRET_KEY',
                'value': '',  # EMPTY - must be set via environment or admin
                'description': 'Django secret key for cryptographic signing. CRITICAL: Must be set via environment variable or admin interface.',
                'category': 'security'
            },
            {
                'key': 'DEBUG',
                'value': '',  # EMPTY - must be set via environment or admin  
                'description': 'Django debug mode (True/False). Should be False in production. Must be set via environment variable or admin interface.',
                'category': 'core'
            },
        ]
        
        # OAuth settings that MUST be configured for authentication
        oauth_settings = [
            {
                'key': 'GOOGLE_OAUTH_CLIENT_ID',
                'value': '',
                'description': 'Google OAuth Client ID for authentication. Required for Google OAuth to work.',
                'category': 'oauth'
            },
            {
                'key': 'GOOGLE_OAUTH_CLIENT_SECRET', 
                'value': '',
                'description': 'Google OAuth Client Secret for authentication. Required for Google OAuth to work.',
                'category': 'oauth'
            },
        ]
        
        # Email settings that MUST be configured for email functionality
        email_settings = [
            {
                'key': 'EMAIL_HOST',
                'value': '',
                'description': 'SMTP server hostname (e.g., smtp.gmail.com). Required for email functionality.',
                'category': 'email'
            },
            {
                'key': 'EMAIL_PORT',
                'value': '',
                'description': 'SMTP server port (e.g., 587 for TLS, 465 for SSL). Required for email functionality.',
                'category': 'email'
            },
            {
                'key': 'EMAIL_USE_TLS',
                'value': '',
                'description': 'Use TLS for email connection (True/False). Required for secure email.',
                'category': 'email'
            },
            {
                'key': 'EMAIL_USE_SSL',
                'value': '',
                'description': 'Use SSL for email connection (True/False). Alternative to TLS.',
                'category': 'email'
            },
            {
                'key': 'EMAIL_HOST_USER',
                'value': '',
                'description': 'SMTP username for authentication. Required for authenticated SMTP.',
                'category': 'email'
            },
            {
                'key': 'EMAIL_HOST_PASSWORD',
                'value': '',
                'description': 'SMTP password for authentication. Required for authenticated SMTP.',
                'category': 'email'
            },
            {
                'key': 'DEFAULT_FROM_EMAIL',
                'value': '',
                'description': 'Default email address for outgoing emails. Required for email functionality.',
                'category': 'email'
            },
        ]
        
        # Domain restriction settings
        domain_settings = [
            {
                'key': 'DOMAIN_RESTRICTION_ENABLED',
                'value': '',
                'description': 'Enable domain restriction for user registration (True/False). Controls access to the platform.',
                'category': 'access_control'
            },
            {
                'key': 'ALLOWED_DOMAIN',
                'value': '',
                'description': 'Allowed email domain for user registration (e.g., coophive.network). Required if domain restriction is enabled.',
                'category': 'access_control'
            },
            {
                'key': 'GOOGLE_VERIFICATION_ENABLED',
                'value': '',
                'description': 'Enable Google account verification for domain users (True/False). Enhances security.',
                'category': 'access_control'
            },
        ]
        
        # Combine all settings
        all_settings = critical_settings + oauth_settings + email_settings + domain_settings
        
        with transaction.atomic():
            created_count = 0
            updated_count = 0
            
            for setting_data in all_settings:
                setting, created = AppSetting.objects.get_or_create(
                    key=setting_data['key'],
                    defaults={
                        'value': setting_data['value'],
                        'description': setting_data['description']
                    }
                )
                
                if created:
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'Created setting: {setting_data["key"]}')
                    )
                elif options['force']:
                    setting.value = setting_data['value']
                    setting.description = setting_data['description'] 
                    setting.save()
                    updated_count += 1
                    self.stdout.write(
                        self.style.WARNING(f'Updated setting: {setting_data["key"]}')
                    )
                else:
                    self.stdout.write(
                        self.style.NOTICE(f'Setting already exists: {setting_data["key"]}')
                    )
            
            # Handle super admin creation
            if options['create_super_admins']:
                self._create_super_admins()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'\nSettings initialization complete:\n'
                    f'- Created: {created_count} settings\n'
                    f'- Updated: {updated_count} settings\n'
                    f'- Total settings: {len(all_settings)}\n\n'
                    f'IMPORTANT: All settings have empty values and MUST be configured via:\n'
                    f'1. Environment variables (recommended for secrets)\n'
                    f'2. Django admin interface (/admin/app_settings/appsetting/)\n\n'
                    f'Critical settings that must be configured:\n'
                    f'- SECRET_KEY (set via environment variable)\n'
                    f'- DEBUG (True for development, False for production)\n'
                    f'- Google OAuth credentials (for authentication)\n'
                    f'- Email settings (for notifications)\n'
                )
            )
    
    def _create_super_admins(self):
        """Create super admin accounts from hardcoded emails."""
        SUPER_ADMIN_EMAILS = ['joe@coophive.network', 'levi@coophive.network']
        
        created_admins = 0
        for email in SUPER_ADMIN_EMAILS:
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'username': email.split('@')[0],
                    'is_staff': True,
                    'is_superuser': True,
                    'is_active': True,
                }
            )
            
            if created:
                # Set an unusable password - force OAuth or password reset
                user.set_unusable_password()
                user.save()
                created_admins += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created super admin: {email}')
                )
            else:
                self.stdout.write(
                    self.style.NOTICE(f'Super admin already exists: {email}')
                )
        
        if created_admins > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f'\nCreated {created_admins} super admin accounts.\n'
                    f'Super admins must use Google OAuth or password reset for first login.'
                )
            )
