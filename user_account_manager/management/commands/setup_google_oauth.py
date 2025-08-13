"""Management command to set up Google OAuth configuration from app_settings."""
from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp
from app_settings.models import SettingsManager

class Command(BaseCommand):
    """Set up Google OAuth configuration using settings from app_settings."""
    
    help = 'Set up or update Google OAuth configuration from app_settings'
    
    def add_arguments(self, parser):
        """Add command line arguments."""
        parser.add_argument(
            '--name',
            type=str,
            default='CoopHive Google OAuth',
            help='Name for the Google OAuth app (default: CoopHive Google OAuth)',
        )
        
    def handle(self, *args, **options):
        """Handle the command execution."""
        # Initialize settings manager
        settings = SettingsManager()
        
        # Get OAuth settings
        client_id = settings.get('GOOGLE_OAUTH_CLIENT_ID')
        client_secret = settings.get('GOOGLE_OAUTH_CLIENT_SECRET')
        
        if not client_id or not client_secret:
            self.stderr.write(self.style.ERROR(
                "Required settings GOOGLE_OAUTH_CLIENT_ID and/or GOOGLE_OAUTH_CLIENT_SECRET not found.\n"
                "Please set up OAuth credentials in Django admin under App Settings first."
            ))
            return
            
        app_name = options['name']
        
        # Ensure we have a site
        site, created = Site.objects.get_or_create(
            pk=1,
            defaults={'domain': 'localhost:8000', 'name': 'CoopHive Local'}
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created site: {site.domain}'))
            
        # Create or update the Google OAuth app
        google_app, created = SocialApp.objects.update_or_create(
            provider='google',
            defaults={
                'name': app_name,
                'client_id': client_id,
                'secret': client_secret,
                'key': '',  # Not used for Google OAuth
            },
        )
        
        # Associate with the site
        google_app.sites.add(site)
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'✅ Created Google OAuth app: {app_name}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'✅ Updated Google OAuth app: {app_name}'))
            
        # Show redirect URIs that need to be configured in Google Cloud Console
        self.stdout.write('\n🔗 Required Google Cloud Console Settings:')
        self.stdout.write('   Authorized redirect URIs:')
        self.stdout.write('   • http://localhost:8000/accounts/google/login/callback/')
        self.stdout.write('   • http://127.0.0.1:8000/accounts/google/login/callback/')
