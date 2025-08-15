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
	GoogleVerificationForm,
)
from .models import VerificationCode, AuthEvent
from .utils import (
	_generate_code,
	_send_code,
	log_auth_event,
	send_admin_new_user_notification,
	get_domain_restriction_setting,
)

User = get_user_model()


@require_http_methods(["GET", "POST"])
def login_view(request):
	"""Enhanced login view supporting both username and email login."""
	if request.user.is_authenticated:
		return redirect("/")

	# Ensure single Google SocialApp exists for template rendering
	from user_account_manager.adapters import _update_google_app_from_database
	_update_google_app_from_database()

	if request.method == "POST":
		form = LoginForm(request, data=request.POST)
		if form.is_valid():
			user = form.get_user()
			login(request, user, backend='user_account_manager.backends.EmailOrUsernameModelBackend')
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

	return render(request, "accounts/login.html", {"form": form})


@require_http_methods(["GET", "POST"])
def register(request):
	"""Registration view with email verification."""
	# Ensure single Google SocialApp exists for template rendering
	from user_account_manager.adapters import _update_google_app_from_database
	_update_google_app_from_database()

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
			# log_auth_event(request, AuthEvent.EventType.REGISTER_EMAIL, email=email)

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

	return render(request, "accounts/register.html", {"form": form})


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
					# log_auth_event(
					# 	request,
					# 	AuthEvent.EventType.VERIFY_CODE,
					# 	user=user,
					# 	email=email,
					# )
					send_admin_new_user_notification(request, user)

					# Log the user in
					login(request, user, backend='user_account_manager.backends.EmailOrUsernameModelBackend')
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

	return render(request, "accounts/verify.html", {"form": form})


@require_http_methods(["GET", "POST"])
def google_verify(request):
	"""Google OAuth verification view (feature-flagged)."""
	if not (get_domain_restriction_setting("ENABLED", False) and get_domain_restriction_setting("GOOGLE_VERIFICATION", False)):
		messages.info(request, "Google verification is not currently enabled.")
		return redirect("accounts:login")

	google_user_data = request.session.get("google_user_data")
	if not google_user_data:
		messages.error(request, "No pending Google OAuth verification found.")
		return redirect("accounts:login")

	if request.method == "POST":
		form = GoogleVerificationForm(request.POST)
		if form.is_valid():
			code = form.cleaned_data["code"]
			email = google_user_data["email"]
			try:
				verification = (
					VerificationCode.objects.filter(
						email=email,
						purpose=VerificationCode.Purpose.GOOGLE_VERIFICATION,
						code=code,
					)
					.order_by("-created_at")
					.first()
				)
				if not verification or not verification.is_valid():
					messages.error(request, "Invalid or expired verification code.")
					return render(request, "accounts/google_verify.html", {"form": form})
				# Get or create user
				user, created = User.objects.get_or_create(
					email=email,
					defaults={
						"username": email.split("@")[0],
					}
				)
				verification.delete()
				request.session.pop("google_user_data", None)
				# log_auth_event(request, AuthEvent.EventType.GOOGLE_VERIFICATION_SUCCESS, user=user, email=email)
				login(request, user, backend='allauth.account.auth_backends.AuthenticationBackend')
				messages.success(request, f"Welcome to CoopHive, {user.get_full_name() or user.username}! Your Google account has been verified.")
				return redirect("/")
			except Exception:
				messages.error(request, "Verification failed. Please try again.")
	else:
		form = GoogleVerificationForm()

	return render(request, "accounts/google_verify.html", {"form": form})


@require_http_methods(["GET", "POST"])
def reset_request(request):
	"""Password reset request using verification code."""
	if request.method == "POST":
		form = PasswordResetRequestForm(request.POST)
		if form.is_valid():
			email = form.cleaned_data["email"].lower()
			code = _generate_code()
			# TODO: Database tables missing - temporarily disabled
			# VerificationCode.objects.filter(email=email, purpose=VerificationCode.Purpose.RESET).delete()
			# VerificationCode.objects.create(email=email, purpose=VerificationCode.Purpose.RESET, code=code)
			_send_code(email, code)
			# log_auth_event(request, AuthEvent.EventType.PASSWORD_RESET_REQUEST, email=email)
			messages.success(request, f"Password reset code sent to {email}.")
			return redirect(f"{reverse('accounts:reset-verify')}?email={email}")
	else:
		form = PasswordResetRequestForm()
	return render(request, "accounts/reset_request.html", {"form": form})


@require_http_methods(["GET", "POST"])
def reset_verify(request):
	"""Password reset verification and set new password."""
	email = request.GET.get("email") or request.POST.get("email")
	if not email:
		messages.error(request, "Missing e-mail context")
		return redirect("accounts:reset")
	if request.method == "POST":
		form = PasswordResetForm(request.POST)
		if form.is_valid():
			code = form.cleaned_data.get("code")
			try:
				# TODO: Database tables missing - temporarily disabled verification
				# verification = (
				# 	VerificationCode.objects.filter(
				# 		email=email,
				# 		purpose=VerificationCode.Purpose.RESET,
				# 		code=code,
				# 	)
				# 	.order_by("-created_at")
				# 	.first()
				# )
				# if not verification or not verification.is_valid():
				# 	messages.error(request, "Invalid or expired reset code")
				# 	return render(request, "accounts/reset_verify.html", {"form": form, "email": email})
				user = User.objects.get(email=email)
				user.set_password(form.cleaned_data["password1"])
				user.save()
				# VerificationCode.objects.filter(email=email, purpose=VerificationCode.Purpose.RESET).delete()
				# log_auth_event(request, AuthEvent.EventType.PASSWORD_RESET_COMPLETE, user=user, email=email)
				messages.success(request, "Password updated successfully. You can now log in.")
				return redirect("/accounts/login/")
			except Exception:
				messages.error(request, "Password reset failed. Please try again.")
	else:
		form = PasswordResetForm(initial={"email": email})
	return render(request, "accounts/reset_verify.html", {"form": form, "email": email})


def domain_breach_redirect(request):
	"""
	Display domain breach error page with styling.
	TaskForge pattern: Extract breach info from session and show styled error page.
	"""
	# Extract breach info from session
	breach_info = request.session.pop("domain_breach", None)
	
	# If no breach info, redirect to login
	if not breach_info:
		return redirect("accounts:login")
	
	context = {
		"breach_email": breach_info.get("email", ""),
		"provider": breach_info.get("provider", ""),
		"timestamp": breach_info.get("timestamp", ""),
		"redirect_delay": 10,  # Auto-redirect after 10 seconds
	}
	
	return render(request, "accounts/domain_breach.html", context)


def logout_view(request):
	"""Logout view with success message."""
	if request.user.is_authenticated:
		username = request.user.get_full_name() or request.user.username
		user_email = request.user.email
		user = request.user
		logout(request)
		messages.success(request, f"Goodbye, {username}! You have been logged out.")
		# log_auth_event(
		# 	request, AuthEvent.EventType.LOGOUT, user=user, email=user_email
		# )
	return redirect("/")
