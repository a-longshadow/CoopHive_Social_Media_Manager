import logging
import random
from typing import Optional

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.http import HttpRequest

from .models import AuthEvent

# Database-first settings manager (imported dynamically to avoid circular imports)

logger = logging.getLogger(__name__)
User = get_user_model()


def _get_setting(key: str, default=None):
	"""Fetch setting from database first (via app_settings), then env, then Django settings."""
	# Database via SettingsManager
	try:
		from app_settings.models import SettingsManager
		val = SettingsManager.get_setting(key, None)
		if val is not None:
			return val
	except Exception:
		pass
	# Environment variable
	import os
	val = os.getenv(key, None)
	if val is not None:
		return val
	# Django settings
	return getattr(settings, key, default)


# Keep backward compatibility
get_setting_db_first = _get_setting


def get_domain_restriction_setting(key: str, default=None):
	"""Database-first domain restriction settings with sane type conversions."""
	map_key = {
		"ENABLED": "DOMAIN_RESTRICTION_ENABLED",
		"ALLOWED_DOMAIN": "ALLOWED_DOMAIN",
		"GOOGLE_VERIFICATION": "GOOGLE_VERIFICATION_ENABLED",
		"BREACH_REDIRECT_DELAY": "BREACH_REDIRECT_DELAY",
		"ADMIN_NOTIFICATION_EMAILS": "ADMIN_NOTIFICATION_EMAILS",
		"LOG_USER_AGENTS": "LOG_USER_AGENTS",
	}.get(key)
	if not map_key:
		return default
	val = _get_setting(map_key, default)
	# Normalize types
	if key in {"ENABLED", "GOOGLE_VERIFICATION", "LOG_USER_AGENTS"}:
		if isinstance(val, bool):
			return val
		return str(val).lower() == "true"
	if key == "BREACH_REDIRECT_DELAY":
		try:
			return int(val)
		except Exception:
			return default
	if key == "ADMIN_NOTIFICATION_EMAILS":
		if isinstance(val, list):
			return val
		return [e.strip() for e in str(val).split(",") if e.strip()]
	return val


def _generate_code() -> str:
	"""Generate a 4-digit verification code."""
	return str(random.randint(1000, 9999))


def _send_code(email: str, code: str):
	"""Send verification code via email."""
	send_mail(
		subject="Your CoopHive verification code",
		message=f"Your verification code is: {code}\n\nThis code will expire in 10 minutes.",
		from_email=settings.DEFAULT_FROM_EMAIL,
		recipient_list=[email],
		fail_silently=False,
	)


def log_auth_event(
	request: HttpRequest,
	event_type: AuthEvent.EventType,
	*,
	user: Optional[User] = None,
	email: str = "",
	extra: dict | None = None,
):
	"""Persist an AuthEvent with IP & user-agent metadata."""
	try:
		AuthEvent.objects.create(
			user=user,
			email=email or (user.email if user else ""),
			event_type=event_type,
			ip_address=request.META.get("REMOTE_ADDR"),
			user_agent=request.META.get("HTTP_USER_AGENT", "")[:512],
			extra=extra,
		)
	except Exception as e:
		logger.error(f"Failed to log auth event: {e}")


def log_domain_breach_attempt(
	request: HttpRequest,
	event_type: str,
	*,
	user: Optional[User] = None,
	email: str = "",
	extra: dict | None = None,
):
	"""Log unauthorized access attempts from non-@coophive.network domains."""
	try:
		if not get_domain_restriction_setting("ENABLED", False):
			return
		AuthEvent.objects.create(
			user=user,
			email=email,
			event_type=event_type,
			ip_address=request.META.get("REMOTE_ADDR"),
			user_agent=request.META.get("HTTP_USER_AGENT", "")[:512],
			extra={
				**(extra or {}),
				"breach_type": "domain_restriction",
				"attempted_email": email,
			},
		)
		logger.warning(f"Domain restriction breach attempt: {email}")
	except Exception as e:
		logger.error(f"Failed to log domain breach: {e}")


def send_admin_new_user_notification(
	request: HttpRequest, user: User, registration_method: str = "email"
):
	"""Send notification to admins when a new user registers."""
	try:
		# Get admin emails from actual superusers, fallback to DB-configured emails
		admin_emails = list(
			User.objects.filter(is_superuser=True, is_active=True)
			.exclude(email="")
			.values_list("email", flat=True)
		)
		if not admin_emails:
			admin_emails = get_domain_restriction_setting("ADMIN_NOTIFICATION_EMAILS", [])
		if not admin_emails:
			logger.warning("No valid admin emails found for new user notification")
			return
		subject = f"New User Registration - {user.get_full_name() or user.email}"
		message = f"""
New User Registration Details:
----------------------------
Name: {user.get_full_name() or 'Not provided'}
Email: {user.email}
Username: {user.username}
Registration Method: {registration_method}
IP Address: {request.META.get('REMOTE_ADDR', 'Unknown')}
Date: {user.date_joined:%Y-%m-%d %H:%M:%S}

User has been automatically added to the standard user group.
"""
		send_mail(
			subject=subject,
			message=message,
			from_email=settings.DEFAULT_FROM_EMAIL,
			recipient_list=admin_emails,
			fail_silently=True,
		)
	except Exception as e:
		logger.error(f"Failed to send admin notification: {e}")


def get_email_settings():
	"""Get email configuration with database-first, env fallback approach. NO hardcoded defaults."""
	def _convert_bool(value):
		"""Convert string/bool to boolean. NO default - raises error if not configured."""
		if isinstance(value, bool):
			return value
		if not value:
			raise ValueError("Email boolean setting must be configured (True/False)")
		return str(value).lower() in ('true', '1', 'yes', 'on')
	
	def _convert_int(value):
		"""Convert string/int to integer. NO default - raises error if not configured."""
		if isinstance(value, int):
			return value
		if not value:
			raise ValueError("Email port setting must be configured (e.g., 587, 465)")
		try:
			return int(value)
		except (ValueError, TypeError):
			raise ValueError(f"Email port must be a valid integer, got: {value}")
	
	# NO hardcoded defaults - all settings must be configured
	try:
		return {
			'EMAIL_HOST': _get_setting('EMAIL_HOST') or os.getenv('EMAIL_HOST'),
			'EMAIL_PORT': _convert_int(_get_setting('EMAIL_PORT') or os.getenv('EMAIL_PORT')),
			'EMAIL_USE_TLS': _convert_bool(_get_setting('EMAIL_USE_TLS') or os.getenv('EMAIL_USE_TLS')),
			'EMAIL_USE_SSL': _convert_bool(_get_setting('EMAIL_USE_SSL') or os.getenv('EMAIL_USE_SSL')),
			'EMAIL_HOST_USER': _get_setting('EMAIL_HOST_USER') or os.getenv('EMAIL_HOST_USER'),
			'EMAIL_HOST_PASSWORD': _get_setting('EMAIL_HOST_PASSWORD') or os.getenv('EMAIL_HOST_PASSWORD'),
			'DEFAULT_FROM_EMAIL': _get_setting('DEFAULT_FROM_EMAIL') or os.getenv('DEFAULT_FROM_EMAIL'),
		}
	except Exception as e:
		raise ValueError(
			f"Email configuration error: {e}\n"
			"All email settings must be configured in database or environment variables:\n"
			"- EMAIL_HOST (e.g., smtp.gmail.com)\n"
			"- EMAIL_PORT (e.g., 587 for TLS, 465 for SSL)\n"
			"- EMAIL_USE_TLS (True/False)\n"
			"- EMAIL_USE_SSL (True/False)\n"
			"- EMAIL_HOST_USER (your email address)\n"
			"- EMAIL_HOST_PASSWORD (your email password/app password)\n"
			"- DEFAULT_FROM_EMAIL (default sender address)"
		)


def is_email_configured():
	"""Check if email is properly configured for sending."""
	config = get_email_settings()
	return bool(config['EMAIL_HOST_USER'] and config['EMAIL_HOST_PASSWORD'])


def get_email_configuration_status():
	"""Get detailed email configuration status for debugging."""
	config = get_email_settings()
	status = {}
	
	for key, value in config.items():
		source = "default"
		
		# Check database first
		try:
			from app_settings.models import SettingsManager
			db_val = SettingsManager.get_setting(key, None)
			if db_val is not None:
				source = "database"
		except Exception:
			pass
		
		# Check environment
		if source == "default":
			import os
			env_val = os.getenv(key)
			if env_val is not None:
				source = "environment"
		
		# Mask sensitive values
		display_value = value
		if key in ['EMAIL_HOST_PASSWORD'] and value:
			display_value = "***"
		
		status[key] = {
			'value': display_value,
			'source': source,
			'configured': bool(value)
		}
	
	return status
