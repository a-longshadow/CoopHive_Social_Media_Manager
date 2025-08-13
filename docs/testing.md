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

## Test Structure

### user_account_manager
- Authentication flows
- Registration process
- Profile management
- Google OAuth integration
- Form validation
- View permissions
- URL routing

### Platform Apps (bluesky, linkedin, twitter, farcaster)
- API integration
- Post creation and scheduling
- Error handling
- Rate limiting
- Media handling
- Analytics tracking

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
from user_account_manager.models import User

class UserRegistrationTests(TestCase):
    def setUp(self):
        self.test_user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_user_registration(self):
        response = self.client.post('/user_account_manager/register/', {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'securepass123',
            'password2': 'securepass123',
        })
        self.assertEqual(response.status_code, 302)  # Redirect after success
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
