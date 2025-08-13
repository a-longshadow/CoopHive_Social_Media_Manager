"""Custom adapters for authentication and social account handling."""
import logging
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialApp
from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse

logger = logging.getLogger(__name__)

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """Custom adapter for social account authentication with domain restriction."""

    def pre_social_login(self, request, sociallogin):
        """Handle pre-login validation and domain restrictions."""
        try:
            # Get email from the social account
            email = sociallogin.account.extra_data.get('email', '')
            
            # Check if domain restriction is enabled
            domain_config = getattr(settings, 'COOPHIVE_DOMAIN_RESTRICTION', {})
            if domain_config.get('ENABLED', False):
                allowed_domain = domain_config.get('ALLOWED_DOMAIN', 'coophive.network')
                
                # Validate email domain
                if not email.endswith(f'@{allowed_domain}'):
                    logger.warning(f'Domain restriction breach attempt: {email}')
                    messages.error(
                        request,
                        f'Only @{allowed_domain} email addresses are allowed to register.'
                    )
                    return redirect(reverse('accounts:domain-breach'))
                
            # If domain is valid or restriction is disabled, proceed with verification
            if domain_config.get('GOOGLE_VERIFICATION', False):
                # Store Google user data in session for verification
                request.session['google_user_data'] = {
                    'email': email,
                    'user_id': sociallogin.user.id if sociallogin.user else None,
                    'name': sociallogin.account.extra_data.get('name', ''),
                }
                
                # Send verification code and redirect to verification page
                from .models import VerificationCode
                code = VerificationCode.create_for_email(
                    email=email,
                    purpose=VerificationCode.Purpose.GOOGLE_VERIFICATION
                )
                code.send()
                
                return redirect(reverse('accounts:google-verify'))
                
        except Exception as e:
            logger.error(f'Error in pre_social_login: {e}')
            messages.error(request, 'An error occurred during social login.')
            return redirect(reverse('accounts:login'))

def _update_google_app_from_database():
    """Update or create Google OAuth app from database settings."""
    try:
        from django.contrib.sites.models import Site
        
        # Get current site
        site = Site.objects.get_current()
        
        # Get credentials from settings
        client_id = settings.SOCIALACCOUNT_PROVIDERS['google']['APP']['client_id']
        client_secret = settings.SOCIALACCOUNT_PROVIDERS['google']['APP']['secret']
        
        if not client_id or not client_secret:
            logger.error('Google OAuth credentials not configured')
            return False
            
        # Create or update the Google OAuth app
        google_app, created = SocialApp.objects.update_or_create(
            provider='google',
            defaults={
                'name': 'CoopHive Google OAuth',
                'client_id': client_id,
                'secret': client_secret,
                'key': '',  # Not used for Google
            }
        )
        
        # Ensure it's associated with the current site
        google_app.sites.clear()
        google_app.sites.add(site)
        
        if created:
            logger.info(f'Created Google OAuth app: {client_id[:20]}...')
        else:
            logger.info(f'Updated Google OAuth app: {client_id[:20]}...')
            
        return True
        
    except Exception as e:
        logger.error(f'Failed to create/update Google app: {e}')
        import traceback
        logger.error(traceback.format_exc())
        
    return False
