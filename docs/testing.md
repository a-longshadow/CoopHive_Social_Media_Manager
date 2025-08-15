# Testing Guide

## Overview

Our test suite covers both unit tests and integration tests for all major components of the application. Tests are organized by Django app and follow the standard Django testing patterns.

## Running Tests

### Full Test Suite
```bash
python manage.py test
```

### App-Specific Tests
```bash
# Test user authentication
python manage.py test user_account_manager

# Test Bluesky integration
python manage.py test bluesky

# Test other platform integrations
python manage.py test linkedin
python manage.py test twitter
python manage.py test farcaster
```

### Coverage Reports
```bash
coverage run manage.py test
coverage report
coverage html  # Generates HTML report
```

## Test Structure by App

### user_account_manager (Authentication Tests)
**Location**: `user_account_manager/tests/test_authentication.py`
**Coverage**: 24 comprehensive authentication tests

#### Test Categories:
- **Login Functionality**: Email/username login, form validation, authentication backends
- **Registration Process**: TaskForge-style forms, domain restrictions, email verification  
- **Google OAuth Integration**: OAuth flow, domain breach handling, social account creation
- **Password Reset Flow**: Reset requests, verification codes, email sending
- **Template Rendering**: Modern TaskForge-styled templates, form rendering
- **Security Features**: Domain restrictions, authentication logging, session security

### twitter (Twitter Integration Tests)
**Location**: `twitter/tests/`

#### Test Categories:
- **Model Testing**: TwitterPost, SourceTweet, CampaignBatch, GeneratedTweet models
- **API Endpoint Testing**: n8n integration endpoints (`/api/check-duplicate-tweet/`, `/api/receive-tweets/`)
- **n8n Integration Testing**: Duplicate detection, campaign storage, date handling
- **View Testing**: Dashboard, scraped tweets interface, campaign review

### Platform Apps (linkedin, farcaster, bluesky)
**Locations**: `{platform}/tests/`

#### Common Test Categories:
- **Model Testing**: Platform-specific post models and validation
- **API Integration**: Platform API connectivity and publishing
- **View Testing**: Dashboard functionality and post management
- **Analytics Testing**: Engagement tracking and reporting

## Writing Tests

### Test Categories
1. Unit Tests
   - Form validation
   - Model methods
   - Utility functions

2. Integration Tests
   - Views
   - API endpoints
   - Authentication flows

3. End-to-End Tests
   - Complete user journeys
   - Platform posting workflows

### Example Test Structure
```python
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()

class LoginTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@coophive.network',
            password='testpass123'
        )

    def test_login_page_loads(self):
        """Test that login page loads correctly with modern styling."""
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Log in to CoopHive')
        self.assertContains(response, 'Continue with Google')  # Google OAuth button

    def test_login_with_email(self):
        """Test successful login with email address."""
        data = {
            'username': 'test@coophive.network',
            'password': 'testpass123'
        }
        response = self.client.post(reverse('accounts:login'), data)
        self.assertEqual(response.status_code, 302)  # Redirect after success

    def test_login_with_username(self):
        """Test successful login with username."""
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(reverse('accounts:login'), data)
        self.assertEqual(response.status_code, 302)  # Redirect after success

class EmailRegistrationTests(TestCase):
    def test_register_page_loads(self):
        """Test that registration page loads with TaskForge styling."""
        response = self.client.get(reverse('accounts:register'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Join CoopHive')
        self.assertContains(response, 'Full name')  # TaskForge field structure

    def test_register_with_valid_data(self):
        """Test successful registration with valid data."""
        data = {
            'email': 'newuser@coophive.network',
            'name': 'New User',
            'username': 'newuser',
            'password1': 'securepass123',
            'password2': 'securepass123'
        }
        response = self.client.post(reverse('accounts:register'), data)
        self.assertEqual(response.status_code, 302)  # Redirect to verification
```

## Continuous Integration

Tests are automatically run on:
- Pull requests
- Merges to main branch
- Pre-deployment checks

## Test Data

Use fixtures or factory_boy for consistent test data:
```bash
# Load test data
python manage.py loaddata test_users.json
python manage.py loaddata test_posts.json
```
