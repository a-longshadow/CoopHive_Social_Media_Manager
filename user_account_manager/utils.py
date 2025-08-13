import logging
import random
from typing import Optional

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.http import HttpRequest

from .models import AuthEvent

logger = logging.getLogger(__name__)
User = get_user_model()


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
        # Get admin emails from actual superusers, fallback to configured emails
        admin_emails = list(
            User.objects.filter(is_superuser=True, is_active=True)
            .exclude(email="")
            .values_list("email", flat=True)
        )

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
