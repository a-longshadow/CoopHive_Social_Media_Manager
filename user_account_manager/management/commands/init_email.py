"""
Management command to initialize and manage email settings.

This command provides utilities to:
- Check current email configuration status
- Set email credentials in database
- Test email sending functionality
- Show configuration sources (database vs environment)
"""

from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from app_settings.manager import SettingsManager


class Command(BaseCommand):
    help = 'Initialize and manage email configuration for CoopHive'

    def add_arguments(self, parser):
        parser.add_argument(
            '--check',
            action='store_true',
            help='Check current email configuration status',
        )
        parser.add_argument(
            '--set-user',
            help='Set EMAIL_HOST_USER in database',
        )
        parser.add_argument(
            '--set-password',
            help='Set EMAIL_HOST_PASSWORD in database',
        )
        parser.add_argument(
            '--set-host',
            help='Set EMAIL_HOST in database (default: smtp.gmail.com)',
        )
        parser.add_argument(
            '--set-from',
            help='Set DEFAULT_FROM_EMAIL in database',
        )
        parser.add_argument(
            '--test',
            help='Send test email to specified address',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear all email settings from database (use environment fallback)',
        )

    def handle(self, *args, **options):
        """Handle command execution."""
        if options['check']:
            self.check_configuration()
        elif options['set_user'] or options['set_password'] or options['set_host'] or options['set_from']:
            self.set_configuration(options)
        elif options['test']:
            self.test_email(options['test'])
        elif options['clear']:
            self.clear_configuration()
        else:
            self.show_help()

    def check_configuration(self):
        """Check and display current email configuration."""
        from user_account_manager.utils import get_email_configuration_status, is_email_configured
        
        self.stdout.write(self.style.SUCCESS('=== Email Configuration Status ==='))
        
        status = get_email_configuration_status()
        
        for key, info in status.items():
            configured_icon = "✅" if info['configured'] else "❌"
            source_color = {
                'database': self.style.SUCCESS,
                'environment': self.style.WARNING,
                'default': self.style.ERROR
            }.get(info['source'], self.style.ERROR)
            
            self.stdout.write(
                f"{configured_icon} {key}: {info['value']} "
                f"({source_color(info['source'])})"
            )
        
        # Overall status
        if is_email_configured():
            self.stdout.write(
                self.style.SUCCESS('\n✅ Email is configured and ready for sending')
            )
            self.stdout.write('Super admins can reset passwords at /accounts/reset/')
        else:
            self.stdout.write(
                self.style.ERROR('\n❌ Email is not configured')
            )
            self.stdout.write('Missing EMAIL_HOST_USER or EMAIL_HOST_PASSWORD')
            self.stdout.write('Super admins must use Google OAuth to log in')

    def set_configuration(self, options):
        """Set email configuration values in database."""
        settings_manager = SettingsManager()
        updated = []
        
        if options['set_user']:
            settings_manager.set('EMAIL_HOST_USER', options['set_user'], 'Email username for SMTP')
            updated.append(f"EMAIL_HOST_USER = {options['set_user']}")
        
        if options['set_password']:
            settings_manager.set('EMAIL_HOST_PASSWORD', options['set_password'], 'Email password for SMTP')
            updated.append("EMAIL_HOST_PASSWORD = ***")
        
        if options['set_host']:
            settings_manager.set('EMAIL_HOST', options['set_host'], 'SMTP server hostname')
            updated.append(f"EMAIL_HOST = {options['set_host']}")
        
        if options['set_from']:
            settings_manager.set('DEFAULT_FROM_EMAIL', options['set_from'], 'Default sender email address')
            updated.append(f"DEFAULT_FROM_EMAIL = {options['set_from']}")
        
        if updated:
            self.stdout.write(self.style.SUCCESS('Updated database settings:'))
            for update in updated:
                self.stdout.write(f'  - {update}')
            
            # Check if email is now configured
            from user_account_manager.utils import is_email_configured
            if is_email_configured():
                self.stdout.write(
                    self.style.SUCCESS('\n✅ Email is now configured!')
                )
                self.stdout.write('You can test it with: python manage.py init_email --test your-email@example.com')
            else:
                self.stdout.write(
                    self.style.WARNING('\n⚠️  Email still needs EMAIL_HOST_USER and EMAIL_HOST_PASSWORD')
                )
        else:
            self.stdout.write(self.style.ERROR('No settings provided to update'))

    def test_email(self, recipient):
        """Send a test email to verify configuration."""
        from user_account_manager.utils import is_email_configured
        
        if not is_email_configured():
            self.stdout.write(
                self.style.ERROR('❌ Email is not configured. Cannot send test email.')
            )
            return
        
        try:
            send_mail(
                subject='CoopHive Email Test',
                message='This is a test email from CoopHive Social Media Manager.\n\nIf you received this, email is working correctly!',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient],
                fail_silently=False,
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ Test email sent successfully to {recipient}')
            )
            self.stdout.write('Check your inbox to confirm delivery.')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Failed to send test email: {str(e)}')
            )
            self.stdout.write('\nCommon issues:')
            self.stdout.write('- Incorrect username or password')
            self.stdout.write('- Gmail requires app passwords (not regular password)')
            self.stdout.write('- SMTP server or port settings incorrect')

    def clear_configuration(self):
        """Clear email settings from database."""
        settings_manager = SettingsManager()
        
        email_keys = [
            'EMAIL_HOST',
            'EMAIL_PORT', 
            'EMAIL_USE_TLS',
            'EMAIL_HOST_USER',
            'EMAIL_HOST_PASSWORD',
            'DEFAULT_FROM_EMAIL'
        ]
        
        cleared = []
        for key in email_keys:
            try:
                # This will remove the setting from database, falling back to environment
                from app_settings.models import AppSetting
                deleted_count = AppSetting.objects.filter(key=key).delete()[0]
                if deleted_count > 0:
                    cleared.append(key)
            except Exception:
                pass
        
        if cleared:
            self.stdout.write(
                self.style.SUCCESS(f'Cleared {len(cleared)} email settings from database:')
            )
            for key in cleared:
                self.stdout.write(f'  - {key}')
            self.stdout.write('\nEmail will now use environment variables or defaults.')
        else:
            self.stdout.write('No email settings found in database to clear.')

    def show_help(self):
        """Show usage examples."""
        self.stdout.write(self.style.SUCCESS('CoopHive Email Configuration'))
        self.stdout.write('\nUsage examples:')
        self.stdout.write('  python manage.py init_email --check')
        self.stdout.write('  python manage.py init_email --set-user "your-email@gmail.com"')
        self.stdout.write('  python manage.py init_email --set-password "your-app-password"')
        self.stdout.write('  python manage.py init_email --test "recipient@example.com"')
        self.stdout.write('  python manage.py init_email --clear')
        self.stdout.write('\nFor Gmail users:')
        self.stdout.write('1. Enable 2-factor authentication')
        self.stdout.write('2. Generate an app password (not your regular password)')
        self.stdout.write('3. Use the app password with --set-password')
        self.stdout.write('\nThe system uses database settings first, then environment variables.')
