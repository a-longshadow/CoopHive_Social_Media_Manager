from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, get_user_model
from django.contrib import messages
from django.utils import timezone
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from .forms import (
    RegisterForm,
    CodeForm,
    LoginForm,
    PasswordResetRequestForm,
    PasswordResetForm,
)
from .models import VerificationCode, AuthEvent
from .utils import (
    _generate_code,
    _send_code,
    log_auth_event,
    send_admin_new_user_notification,
)

User = get_user_model()


@require_http_methods(["GET", "POST"])
def login_view(request):
    """Enhanced login view supporting both username and email login."""
    if request.user.is_authenticated:
        return redirect("/")

    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            log_auth_event(
                request, AuthEvent.EventType.LOGIN_EMAIL, user=user, email=user.email
            )

            welcome_name = user.get_full_name() or user.username
            messages.success(
                request,
                f"Welcome back, {welcome_name}! You're now logged into CoopHive.",
            )

            return redirect(request.GET.get("next", "/"))
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = LoginForm()

        return render(request, "user_account_manager/reset_otp.html", {"form": form})


@require_http_methods(["GET", "POST"])
def register(request):
    """Registration view with email verification."""
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"].lower()
            password = form.cleaned_data["password1"]
            username = email.split("@")[0]
            full_name = form.cleaned_data.get("full_name", "")
            code = _generate_code()

            # Delete any existing signup codes
            VerificationCode.objects.filter(
                email=email, purpose=VerificationCode.Purpose.SIGNUP
            ).delete()

            # Create verification code
            VerificationCode.objects.create(
                email=email,
                purpose=VerificationCode.Purpose.SIGNUP,
                code=code,
            )

            _send_code(email, code)
            log_auth_event(request, AuthEvent.EventType.REGISTER_EMAIL, email=email)

            # Store registration data in session
            request.session["registration_data"] = {
                "email": email,
                "password": password,
                "username": username,
                "full_name": full_name,
            }

            messages.success(
                request,
                f"We've sent a verification code to {email}. Please check your inbox and enter the code to complete your registration.",
            )

            return redirect(reverse("accounts:verify"))
    else:
        form = RegisterForm()

    return render(request, "user_account_manager/register.html", {"form": form})


@require_http_methods(["GET", "POST"])
def verify(request):
    """Verification view for completing registration."""
    registration_data = request.session.get("registration_data")
    if not registration_data:
        messages.error(request, "No pending registration found.")
        return redirect("accounts:register")

    if request.method == "POST":
        form = CodeForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data["code"]
            email = registration_data["email"]

            try:
                verification = VerificationCode.objects.get(
                    email=email,
                    purpose=VerificationCode.Purpose.SIGNUP,
                    code=code,
                )

                if verification.is_valid():
                    # Create the user
                    user = User.objects.create_user(
                        username=registration_data["username"],
                        email=email,
                        password=registration_data["password"],
                    )

                    if registration_data["full_name"]:
                        name_parts = registration_data["full_name"].split(maxsplit=1)
                        user.first_name = name_parts[0]
                        if len(name_parts) > 1:
                            user.last_name = name_parts[1]
                        user.save()

                    # Clean up
                    verification.delete()
                    del request.session["registration_data"]

                    # Log verification and notify admin
                    log_auth_event(
                        request,
                        AuthEvent.EventType.VERIFY_CODE,
                        user=user,
                        email=email,
                    )
                    send_admin_new_user_notification(request, user)

                    # Log the user in
                    login(request, user)
                    messages.success(
                        request,
                        f"Welcome to CoopHive, {user.get_full_name() or user.username}! Your account has been created and you're now logged in.",
                    )
                    return redirect("/")
                else:
                    messages.error(
                        request, "This verification code has expired. Please register again."
                    )
                    return redirect("accounts:register")

            except VerificationCode.DoesNotExist:
                messages.error(request, "Invalid verification code.")
        else:
            messages.error(request, "Please enter a valid 4-digit code.")
    else:
        form = CodeForm()

    return render(request, "user_account_manager/verify_otp.html", {"form": form})


def logout_view(request):
    """Logout view with success message."""
    if request.user.is_authenticated:
        username = request.user.get_full_name() or request.user.username
        logout(request)
        messages.success(request, f"Goodbye, {username}! You have been logged out.")
        log_auth_event(
            request, AuthEvent.EventType.LOGOUT, email=request.user.email
        )
    return redirect("/")
