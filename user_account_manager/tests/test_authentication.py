"""
Comprehensive authentication system tests.
Based on TaskForge testing patterns.
"""

import pytest
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core import mail
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp

from user_account_manager.models import VerificationCode, AuthEvent
from user_account_manager.forms import RegisterForm, LoginForm, CodeForm

User = get_user_model()


class AuthenticationTestCase(TestCase):
    """Base test case for authentication tests."""
    
    def setUp(self):
        self.client = Client()
        self.site = Site.objects.get_current()
        
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@coophive.network',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        # Ensure a single Google OAuth app is present and attached to current site
        SocialApp.objects.filter(provider='google').delete()
        self.google_app, _ = SocialApp.objects.update_or_create(
            provider='google',
            defaults={
                'name': 'Test Google OAuth',
                'client_id': 'test-client-id',
                'secret': 'test-client-secret',
                'key': ''
            }
        )
        self.google_app.sites.set([self.site])


class EmailRegistrationTests(AuthenticationTestCase):
    """Test email-based registration flow."""
    
    def test_register_page_loads(self):
        """Test that registration page loads correctly."""
        response = self.client.get(reverse('accounts:register'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Join CoopHive')
    
    def test_register_with_valid_data(self):
        """Test successful registration with valid data."""
        data = {
            'email': 'newuser@coophive.network',
            'password1': 'newpass123',
            'password2': 'newpass123',
            'full_name': 'New User'
        }
        response = self.client.post(reverse('accounts:register'), data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('accounts:verify'))
        
        # Check that verification code was created
        self.assertTrue(VerificationCode.objects.filter(
            email='newuser@coophive.network',
            purpose=VerificationCode.Purpose.SIGNUP
        ).exists())
        
        # Check that email was sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('verification code', mail.outbox[0].subject)
    
    def test_register_with_invalid_domain(self):
        """Test registration rejection for non-coophive.network emails."""
        data = {
            'email': 'user@gmail.com',
            'password1': 'newpass123',
            'password2': 'newpass123',
            'full_name': 'New User'
        }
        response = self.client.post(reverse('accounts:register'), data)
        self.assertEqual(response.status_code, 200)  # Form errors, no redirect
        self.assertContains(response, 'coophive.network')
    
    def test_register_with_existing_email(self):
        """Test registration rejection for existing email."""
        data = {
            'email': 'test@coophive.network',  # Already exists
            'password1': 'newpass123',
            'password2': 'newpass123',
            'full_name': 'New User'
        }
        response = self.client.post(reverse('accounts:register'), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'already exists')
    
    def test_register_with_mismatched_passwords(self):
        """Test registration rejection for mismatched passwords."""
        data = {
            'email': 'newuser@coophive.network',
            'password1': 'newpass123',
            'password2': 'differentpass',
            'full_name': 'New User'
        }
        response = self.client.post(reverse('accounts:register'), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'do not match')


class EmailVerificationTests(AuthenticationTestCase):
    """Test email verification flow."""
    
    def setUp(self):
        super().setUp()
        # Create verification code
        self.verification_code = VerificationCode.objects.create(
            email='newuser@coophive.network',
            purpose=VerificationCode.Purpose.SIGNUP,
            code='1234'
        )
        
        # Set up session data
        session = self.client.session
        session['registration_data'] = {
            'email': 'newuser@coophive.network',
            'password': 'newpass123',
            'username': 'newuser',
            'full_name': 'New User'
        }
        session.save()
    
    def test_verify_page_loads(self):
        """Test that verification page loads correctly."""
        response = self.client.get(reverse('accounts:verify'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Enter Verification Code')
    
    def test_verify_with_valid_code(self):
        """Test successful verification with valid code."""
        data = {'code': '1234'}
        response = self.client.post(reverse('accounts:verify'), data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/')
        
        # Check that user was created
        user = User.objects.get(email='newuser@coophive.network')
        self.assertEqual(user.username, 'newuser')
        self.assertEqual(user.first_name, 'New')
        self.assertEqual(user.last_name, 'User')
        
        # Check that verification code was deleted
        self.assertFalse(VerificationCode.objects.filter(code='1234').exists())
        
        # Check that auth event was logged
        self.assertTrue(AuthEvent.objects.filter(
            event_type=AuthEvent.EventType.VERIFY_CODE,
            user=user
        ).exists())
    
    def test_verify_with_invalid_code(self):
        """Test verification rejection with invalid code."""
        data = {'code': '9999'}
        response = self.client.post(reverse('accounts:verify'), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid verification code')
    
    def test_verify_with_expired_code(self):
        """Test verification rejection with expired code."""
        # Manually expire the code
        from django.utils import timezone
        from datetime import timedelta
        self.verification_code.created_at = timezone.now() - timedelta(minutes=15)
        self.verification_code.save()
        
        data = {'code': '1234'}
        response = self.client.post(reverse('accounts:verify'), data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('accounts:register'))


class LoginTests(AuthenticationTestCase):
    """Test login functionality."""
    
    def test_login_page_loads(self):
        """Test that login page loads correctly."""
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Log in to CoopHive')
    
    def test_login_with_valid_credentials(self):
        """Test successful login with valid credentials."""
        data = {
            'username': 'test@coophive.network',
            'password': 'testpass123'
        }
        response = self.client.post(reverse('accounts:login'), data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/')
        
        # Check that user is logged in
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        
        # Check that auth event was logged
        self.assertTrue(AuthEvent.objects.filter(
            event_type=AuthEvent.EventType.LOGIN_EMAIL,
            user=self.user
        ).exists())
    
    def test_login_with_invalid_credentials(self):
        """Test login rejection with invalid credentials."""
        data = {
            'username': 'test@coophive.network',
            'password': 'wrongpassword'
        }
        response = self.client.post(reverse('accounts:login'), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid username or password')
    
    def test_login_with_username(self):
        """Test login with username instead of email."""
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(reverse('accounts:login'), data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/')


class LogoutTests(AuthenticationTestCase):
    """Test logout functionality."""
    
    def test_logout_when_logged_in(self):
        """Test successful logout when user is logged in."""
        self.client.force_login(self.user)
        response = self.client.get(reverse('accounts:logout'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/')
        
        # Check that user is logged out
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        
        # Check that auth event was logged
        self.assertTrue(AuthEvent.objects.filter(
            event_type=AuthEvent.EventType.LOGOUT,
            user=self.user
        ).exists())
    
    def test_logout_when_not_logged_in(self):
        """Test logout when user is not logged in."""
        response = self.client.get(reverse('accounts:logout'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/')


class GoogleOAuthTests(AuthenticationTestCase):
    """Test Google OAuth integration."""
    
    def test_google_verify_page_loads(self):
        """Test that Google verification page loads correctly."""
        # Set up session data
        session = self.client.session
        session['google_user_data'] = {
            'email': 'test@coophive.network',
            'name': 'Test User'
        }
        session.save()
        
        response = self.client.get(reverse('accounts:google-verify'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Verify Your Google Account')
    
    def test_google_verify_without_session(self):
        """Test Google verification redirect when no session data."""
        response = self.client.get(reverse('accounts:google-verify'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('accounts:login'))


class DomainBreachTests(AuthenticationTestCase):
    """Test domain restriction functionality."""
    
    def test_domain_breach_redirect(self):
        """Test domain breach redirect page."""
        response = self.client.get(reverse('accounts:domain-breach'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('accounts:login'))


class FormTests(AuthenticationTestCase):
    """Test form validation."""
    
    def test_register_form_validation(self):
        """Test RegisterForm validation."""
        # Valid data
        form_data = {
            'email': 'newuser@coophive.network',
            'password1': 'newpass123',
            'password2': 'newpass123',
            'full_name': 'New User'
        }
        form = RegisterForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        # Invalid domain
        form_data['email'] = 'user@gmail.com'
        form = RegisterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('coophive.network', str(form.errors))
        
        # Mismatched passwords
        form_data['email'] = 'newuser@coophive.network'
        form_data['password2'] = 'differentpass'
        form = RegisterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('do not match', str(form.errors))
    
    def test_code_form_validation(self):
        """Test CodeForm validation."""
        # Valid code
        form = CodeForm(data={'code': '1234'})
        self.assertTrue(form.is_valid())
        
        # Invalid code (non-numeric)
        form = CodeForm(data={'code': 'abcd'})
        self.assertFalse(form.is_valid())
        self.assertIn('digits', str(form.errors))
        
        # Invalid code (wrong length)
        form = CodeForm(data={'code': '123'})
        self.assertFalse(form.is_valid())


class ModelTests(AuthenticationTestCase):
    """Test model functionality."""
    
    def test_verification_code_creation(self):
        """Test VerificationCode.create_for_email method."""
        code = VerificationCode.create_for_email(
            email='test@coophive.network',
            purpose=VerificationCode.Purpose.SIGNUP
        )
        self.assertIsInstance(code, VerificationCode)
        self.assertEqual(code.email, 'test@coophive.network')
        self.assertEqual(code.purpose, VerificationCode.Purpose.SIGNUP)
        self.assertTrue(code.is_valid())
    
    def test_verification_code_expiration(self):
        """Test VerificationCode expiration."""
        code = VerificationCode.objects.create(
            email='test@coophive.network',
            purpose=VerificationCode.Purpose.SIGNUP,
            code='1234'
        )
        self.assertTrue(code.is_valid())
        
        # Manually expire the code
        from django.utils import timezone
        from datetime import timedelta
        code.created_at = timezone.now() - timedelta(minutes=15)
        code.save()
        self.assertFalse(code.is_valid())
    
    def test_auth_event_creation(self):
        """Test AuthEvent creation."""
        event = AuthEvent.objects.create(
            user=self.user,
            email=self.user.email,
            event_type=AuthEvent.EventType.LOGIN_EMAIL,
            ip_address='127.0.0.1',
            user_agent='Test Browser'
        )
        self.assertIsInstance(event, AuthEvent)
        self.assertEqual(event.user, self.user)
        self.assertEqual(event.event_type, AuthEvent.EventType.LOGIN_EMAIL)


class URLTests(AuthenticationTestCase):
    """Test URL resolution."""
    
    def test_url_namespaces(self):
        """Test that all URLs resolve correctly."""
        urls_to_test = [
            ('accounts:login', '/accounts/login/'),
            ('accounts:logout', '/accounts/logout/'),
            ('accounts:register', '/accounts/register/'),
            ('accounts:verify', '/accounts/verify/'),
            ('accounts:google-verify', '/accounts/google/verify/'),
            ('accounts:domain-breach', '/accounts/domain-breach/'),
        ]
        
        for url_name, expected_path in urls_to_test:
            resolved_url = reverse(url_name)
            self.assertEqual(resolved_url, expected_path)


@pytest.mark.django_db
class IntegrationTests:
    """Integration tests using pytest."""
    
    def test_complete_registration_flow(self, client):
        """Test complete registration flow from start to finish."""
        # Step 1: Register
        register_data = {
            'email': 'integration@coophive.network',
            'password1': 'integration123',
            'password2': 'integration123',
            'full_name': 'Integration Test'
        }
        response = client.post(reverse('accounts:register'), register_data)
        assert response.status_code == 302
        assert response.url == reverse('accounts:verify')
        
        # Step 2: Get verification code
        verification_code = VerificationCode.objects.get(
            email='integration@coophive.network',
            purpose=VerificationCode.Purpose.SIGNUP
        )
        
        # Step 3: Verify
        verify_data = {'code': verification_code.code}
        response = client.post(reverse('accounts:verify'), verify_data)
        assert response.status_code == 302
        assert response.url == '/'
        
        # Step 4: Verify user was created and logged in
        user = User.objects.get(email='integration@coophive.network')
        assert user.username == 'integration'
        assert user.first_name == 'Integration'
        assert user.last_name == 'Test'
    
    def test_complete_login_flow(self, client):
        """Test complete login flow."""
        # Create user
        user = User.objects.create_user(
            username='logintest',
            email='logintest@coophive.network',
            password='logintest123'
        )
        
        # Login
        login_data = {
            'username': 'logintest@coophive.network',
            'password': 'logintest123'
        }
        response = client.post(reverse('accounts:login'), login_data)
        assert response.status_code == 302
        assert response.url == '/'
        
        # Verify user is logged in
        assert response.wsgi_request.user.is_authenticated
        assert response.wsgi_request.user == user
