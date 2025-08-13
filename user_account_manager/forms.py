from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError

from .models import VerificationCode

User = get_user_model()


def _validate_domain(email: str):
    """Validate that the email belongs to @coophive.network domain."""
    if not email.lower().endswith("@coophive.network"):
        raise ValidationError(
            "Sorry, registration is only allowed with a @coophive.network email address."
        )


class RegisterForm(forms.Form):
    """Registration form with email domain validation."""
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={"class": "w-full border border-gray-300 rounded p-2", 
                  "placeholder": "yourname@coophive.network"}
        )
    )
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs={"class": "w-full border border-gray-300 rounded p-2"}
        ),
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(
            attrs={"class": "w-full border border-gray-300 rounded p-2"}
        ),
    )
    full_name = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"class": "w-full border border-gray-300 rounded p-2",
                  "placeholder": "Your full name"}
        ),
    )

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        _validate_domain(email)
        if User.objects.filter(email=email).exists():
            raise ValidationError("User with this e-mail already exists")
        return email

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("password1") != cleaned.get("password2"):
            raise ValidationError("Passwords do not match")
        return cleaned


class CodeForm(forms.Form):
    """Form for entering 4-digit verification codes."""
    code = forms.CharField(
        max_length=4,
        min_length=4,
        widget=forms.TextInput(
            attrs={
                "class": "w-full text-center font-mono text-2xl border border-gray-300 rounded p-2",
                "placeholder": "0000"
            }
        ),
    )

    def clean_code(self):
        code = self.cleaned_data["code"]
        if not code.isdigit():
            raise ValidationError("Code must contain only digits")
        return code


class LoginForm(AuthenticationForm):
    """Custom login form supporting both username and email login."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Username or Email"
        self.fields["username"].widget.attrs.update(
            {
                "placeholder": "Enter your username or email",
                "class": "w-full border border-gray-300 rounded p-2",
            }
        )
        self.fields["password"].widget.attrs.update(
            {"class": "w-full border border-gray-300 rounded p-2"}
        )


class PasswordResetRequestForm(forms.Form):
    """Form for requesting a password reset."""
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={"class": "w-full border border-gray-300 rounded p-2"}
        )
    )

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        _validate_domain(email)
        if not User.objects.filter(email=email).exists():
            raise ValidationError("No user found with this email address")
        return email


class PasswordResetForm(forms.Form):
    """Form for setting a new password after reset."""
    password1 = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(
            attrs={"class": "w-full border border-gray-300 rounded p-2"}
        ),
    )
    password2 = forms.CharField(
        label="Confirm New Password",
        widget=forms.PasswordInput(
            attrs={"class": "w-full border border-gray-300 rounded p-2"}
        ),
    )

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("password1") != cleaned.get("password2"):
            raise ValidationError("Passwords do not match")
        return cleaned
