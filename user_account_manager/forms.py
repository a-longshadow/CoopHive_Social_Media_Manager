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
    email = forms.EmailField()
    name = forms.CharField(required=False, max_length=150, label="Full name")
    username = forms.CharField(required=False, max_length=150)
    password1 = forms.CharField(widget=forms.PasswordInput())
    password2 = forms.CharField(widget=forms.PasswordInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].widget.attrs["placeholder"] = "yourname@coophive.network"
        self.fields["password1"].label = "Password"
        self.fields["password2"].label = "Confirm password"
        self.fields["password1"].widget.attrs["placeholder"] = "Create a strong password"
        self.fields["password2"].widget.attrs["placeholder"] = "Re-enter password"
        self.fields["password1"].widget.attrs["autocomplete"] = "new-password"
        self.fields["password2"].widget.attrs["autocomplete"] = "new-password"
        
        # Set default CSS classes for all fields
        for field in self.fields.values():
            field.widget.attrs.setdefault(
                "class", "w-full border border-gray-300 rounded p-2"
            )

        self.fields["name"].widget.attrs["placeholder"] = "Your full name (optional)"
        self.fields["username"].widget.attrs["placeholder"] = "username (optional)"

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        _validate_domain(email)
        if User.objects.filter(email=email).exists():
            raise ValidationError("User with this e-mail already exists")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords do not match")
        
        return cleaned_data


class CodeForm(forms.Form):
    """Form for entering 4-digit verification codes."""
    code = forms.CharField(max_length=4, min_length=4)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["code"].widget.attrs["placeholder"] = "1234"
        self.fields["code"].widget.attrs["class"] = "w-full text-center text-3xl font-mono tracking-widest border border-gray-300 rounded p-2"

    def clean_code(self):
        code = self.cleaned_data["code"]
        if not code.isdigit():
            raise ValidationError("Code must contain only digits")
        return code


class GoogleVerificationForm(forms.Form):
    """Form for Google OAuth verification codes."""
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
        
        # Customize the username field to indicate it accepts email too
        self.fields["username"].label = "Username or Email"
        self.fields["username"].widget.attrs.update(
            {
                "placeholder": "Enter your username or email",
                "class": "w-full border border-gray-300 rounded p-2",
            }
        )
        
        # Update password field
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
    code = forms.CharField(
        label="Reset Code",
        max_length=4,
        min_length=4,
        widget=forms.TextInput(
            attrs={
                "class": "w-full text-center font-mono text-2xl border border-gray-300 rounded p-2",
                "placeholder": "0000"
            }
        ),
    )
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
