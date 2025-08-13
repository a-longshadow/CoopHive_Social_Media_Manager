from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import uuid

User = get_user_model()

class VerificationCode(models.Model):
    """Stores short-lived 4-digit codes for signup & password-reset."""

    class Purpose(models.TextChoices):
        SIGNUP = "signup", "Signup"
        RESET = "reset", "Password Reset"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField()
    code = models.CharField(max_length=4)
    purpose = models.CharField(max_length=20, choices=Purpose.choices)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=["email", "purpose"])]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.email} – {self.code} ({self.purpose})"

    def is_valid(self):
        return timezone.now() < self.created_at + timedelta(minutes=10)


class AuthEvent(models.Model):
    """Stores authentication-related events for analytics & auditing."""

    class EventType(models.TextChoices):
        REGISTER_EMAIL = "register_email", "Register (E-mail)"
        LOGIN_EMAIL = "login_email", "Login (E-mail)"
        LOGOUT = "logout", "Logout"
        VERIFY_CODE = "verify_code", "Verification Code"
        PASSWORD_RESET_REQUEST = "password_reset_request", "Password Reset Request"
        PASSWORD_RESET_COMPLETE = "password_reset_complete", "Password Reset Complete"
        REGISTER_EMAIL_BREACH = "register_email_breach", "Registration Breach (Email)"
        PASSWORD_RESET_BREACH = "password_reset_breach", "Password Reset Breach"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    email = models.EmailField(blank=True)
    event_type = models.CharField(max_length=40, choices=EventType.choices)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=512, blank=True)
    extra = models.JSONField(blank=True, null=True)

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["event_type", "timestamp"]),
            models.Index(fields=["email"]),
        ]

    def __str__(self):
        who = self.user or self.email or "anon"
        return f"{self.timestamp:%Y-%m-%d %H:%M:%S} • {self.event_type} • {who}"
