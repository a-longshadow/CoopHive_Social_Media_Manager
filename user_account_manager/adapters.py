"""Custom adapters for authentication and social account handling."""
import logging
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialApp
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse

from .models import VerificationCode, AuthEvent
from .utils import log_auth_event, log_domain_breach_attempt, get_domain_restriction_setting, get_setting_db_first

logger = logging.getLogger(__name__)


def _update_google_app_from_database() -> bool:
	"""Create/update Google SocialApp from DB-first credentials and attach to current site.

	- Fetch client_id/secret from DB (fallback env/settings)
	- Clean duplicates
	- Attach to current Site
	"""
	try:
		from django.contrib.sites.models import Site
		client_id = get_setting_db_first("GOOGLE_OAUTH_CLIENT_ID", "")
		client_secret = get_setting_db_first("GOOGLE_OAUTH_CLIENT_SECRET", "")
		if not client_id or not client_secret:
			logger.warning("Google OAuth credentials not configured in database/env/settings")
			return False
		site = Site.objects.get_current()
		# Clean duplicates
		existing = SocialApp.objects.filter(provider="google")
		if existing.count() > 1:
			keeper = existing.first()
			existing.exclude(pk=keeper.pk).delete()
		# Upsert
		google_app, _ = SocialApp.objects.update_or_create(
			provider="google",
			defaults={
				"name": "CoopHive Google OAuth",
				"client_id": client_id,
				"secret": client_secret,
				"key": "",
			},
		)
		google_app.sites.set([site])
		return True
	except Exception as e:
		logger.error(f"Failed to update Google SocialApp: {e}")
		return False


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
	"""Custom adapter for social account authentication with domain restriction."""

	def pre_social_login(self, request, sociallogin):
		"""
		Hook called before social login to handle existing users.
		TaskForge pattern: Only handle user connection, NO domain restrictions here.
		"""
		# Update Google app from database before allauth tries to use it
		if sociallogin.account.provider == "google":
			_update_google_app_from_database()
		
		# Try to connect to existing user account by email
		if sociallogin.is_existing:
			return

		if sociallogin.account.provider == "google":
			email = sociallogin.account.extra_data.get("email")
			if email:
				# Check if user with this email already exists
				from django.contrib.auth import get_user_model

				User = get_user_model()

				try:
					existing_user = User.objects.get(email=email)
					# Connect the social account to the existing user
					sociallogin.connect(request, existing_user)
					logger.info(f"Connected Google account to existing user: {email}")
				except User.DoesNotExist:
					# New user - will be handled in save_user
					pass

	def save_user(self, request, sociallogin, form=None):
		"""
		Handle user creation with domain restrictions.
		TaskForge pattern: Domain restrictions handled here, not in pre_social_login.
		"""
		from django.contrib.auth import get_user_model
		from django.utils import timezone

		User = get_user_model()
		
		# Get user data from sociallogin
		email = sociallogin.account.extra_data.get("email", "")
		name = sociallogin.account.extra_data.get("name", "")
		
		# Check domain restrictions
		allowed_enabled = get_domain_restriction_setting("ENABLED", False)
		allowed_domain = get_domain_restriction_setting("ALLOWED_DOMAIN", "coophive.network")
		google_verification = get_domain_restriction_setting("GOOGLE_VERIFICATION", False)
		
		# Use the sociallogin.user object instead of creating new User
		user = sociallogin.user
		user.email = email
		user.username = email  # Use email as username
		user.first_name = name.split()[0] if name else ""
		user.last_name = " ".join(name.split()[1:]) if name and len(name.split()) > 1 else ""
		
		if allowed_enabled and not email.endswith(f"@{allowed_domain}"):
			# Domain restriction breach - create disabled user and store breach info
			user.is_active = False
			user.save()
			
			# Log security breach attempt
			log_domain_breach_attempt(
				request,
				AuthEvent.EventType.GOOGLE_OAUTH_BREACH,
				user=user,
				email=email,
				extra={
					"provider": "google",
					"oauth_uid": sociallogin.account.uid,
				},
			)
			
			# Store breach info in session for custom redirect
			request.session["domain_breach"] = {
				"email": email,
				"provider": "google",
				"timestamp": timezone.now().isoformat(),
			}
			
			logger.warning(f"Domain restriction breach via Google OAuth: {email}")
			return user
			
		# Valid domain - check if Google verification is required
		elif google_verification:
			# Store Google user data in session for verification
			request.session["google_user_data"] = {
				"email": email,
				"user_id": None,  # Will be set after user creation
				"name": name,
			}
			
			# Send verification code
			code = VerificationCode.create_for_email(
				email=email,
				purpose=VerificationCode.Purpose.GOOGLE_VERIFICATION,
			)
			code.send()
			log_auth_event(request, AuthEvent.EventType.GOOGLE_VERIFICATION_SENT, email=email)
			
			# Create active user (verification will be handled in redirect)
			user.is_active = True
			user.save()
			
			# Update session with user ID
			request.session["google_user_data"]["user_id"] = user.id
			
			return user
		else:
			# No restrictions - create active user
			user.is_active = True
			user.save()
			logger.info(f"Created new user via Google OAuth: {email}")
			return user

	def get_login_redirect_url(self, request):
		"""
		Enhanced redirect with domain restriction and verification support.
		TaskForge pattern: Check session and redirect to appropriate page.
		"""
		# Check for domain breach redirect
		if request.session.get("domain_breach"):
			return reverse("accounts:domain-breach")

		# Check for Google verification redirect
		google_data = request.session.get("google_user_data")
		if google_data:
			# User needs to verify their Google email
			messages.info(
				request,
				f"Please verify your email address. We've sent a verification code to {google_data.get('email')}.",
			)
			return reverse("accounts:google-verify")

		# Use our standard redirect logic
		return request.GET.get("next", "/")

	def on_authentication_error(
		self, request, provider_id, error=None, exception=None, extra_context=None
	):
		"""
		Handle authentication errors with proper messaging.
		Updated method name to fix deprecation warning.
		"""
		logger.error(f"Google OAuth error: {error} - {exception}")
		# Clear any existing messages to avoid avalanche
		list(messages.get_messages(request))
		messages.error(
			request, "Google sign-in failed. Please try again or use email login."
		)

	def is_auto_signup_allowed(self, request, sociallogin):
		"""
		Force auto-signup to skip intermediate signup form completely.
		TaskForge pattern: Always allow auto-signup for smooth flow.
		"""
		return True

	def add_message(
		self, request, level, message_template, message_context=None, extra_tags=""
	):
		"""
		Add messages using our enhanced messaging system.
		TaskForge pattern: Let the view handle the welcome message to maintain consistency.
		"""
		# Let the view handle the welcome message to maintain consistency
		pass
