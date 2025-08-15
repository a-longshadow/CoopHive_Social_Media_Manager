# Database Models Documentation

## Overview

This document details all database models across the application's Django apps, including the core models, user management, settings, and platform-specific models.

## User Account Manager

### User Model
The application uses Django's built-in User model with custom authentication backends:

```python
# Uses Django's default User model with these custom features:
# - Email-based login (EmailOrUsernameModelBackend)
# - Google OAuth integration via django-allauth
# - Domain restriction (@coophive.network only)
# - Hardcoded super admins (joe@coophive.network, levi@coophive.network)
```

### VerificationCode Model
```python
class VerificationCode(models.Model):
    PURPOSE_CHOICES = [
        ('EMAIL_VERIFICATION', 'Email Verification'),
        ('PASSWORD_RESET', 'Password Reset'),
        ('GOOGLE_VERIFICATION', 'Google OAuth Verification'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=4)
    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)
    
    @classmethod
    def create_for_email(cls, user, purpose):
        # Generates 4-digit verification codes
    
    def send(self):
        # Sends verification code via email
```

### AuthEvent Model
```python
class AuthEvent(models.Model):
    EVENT_TYPES = [
        ('LOGIN_SUCCESS', 'Login Success'),
        ('LOGIN_FAILURE', 'Login Failure'),
        ('GOOGLE_OAUTH_SUCCESS', 'Google OAuth Success'),
        ('GOOGLE_OAUTH_BREACH', 'Google OAuth Domain Breach'),
        ('PASSWORD_RESET_REQUEST', 'Password Reset Request'),
        ('EMAIL_VERIFICATION_SENT', 'Email Verification Sent'),
        # ... more event types
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    event_type = models.CharField(max_length=30, choices=EVENT_TYPES)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    metadata = models.JSONField(default=dict)
    timestamp = models.DateTimeField(auto_now_add=True)
```

## App Settings

### AppSetting Model
Database-first configuration management:

```python
class AppSetting(models.Model):
    key = models.CharField(max_length=100, unique=True, db_index=True)
    value = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Setting'
        verbose_name_plural = 'Settings'
        ordering = ['key']
```

### SettingsManager
```python
class SettingsManager:
    @staticmethod
    def get_setting(key, default=None):
        # Retrieves setting from database
    
    @staticmethod
    def set_setting(key, value):
        # Stores setting in database
```

## Core Models

### Campaign Model
```python
class Campaign(models.Model):
    name = models.CharField(max_length=200)
    platform = models.CharField(max_length=50)
    status = models.CharField(max_length=20)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    total_posts = models.IntegerField(default=0)
    total_engagement = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### Post Model (Base)
```python
class Post(models.Model):
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    platform = models.CharField(max_length=50)
    status = models.CharField(max_length=20)
    scheduled_time = models.DateTimeField(null=True, blank=True)
    published_time = models.DateTimeField(null=True, blank=True)
    platform_post_id = models.CharField(max_length=100, blank=True)
    
    # Engagement metrics
    likes = models.IntegerField(default=0)
    shares = models.IntegerField(default=0)
    comments = models.IntegerField(default=0)
    views = models.IntegerField(default=0)
    
    # Additional fields
    hashtags = models.TextField(blank=True)
    mentions = models.TextField(blank=True)
    media_urls = models.TextField(blank=True)
    campaign = models.ForeignKey(Campaign, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        abstract = False  # This is a concrete model
        ordering = ['-created_at']
```

### MediaAsset Model
```python
class MediaAsset(models.Model):
    file_path = models.CharField(max_length=500, blank=True, default='')
    file_type = models.CharField(max_length=50)
    file_size = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
```

## Platform Models

All platform-specific models inherit from the base `Post` model in the `core` app.

### Twitter Models

#### TwitterPost Model
```python
class TwitterPost(Post):
    """Twitter (X.com) specific post model"""
    # Twitter-specific fields
    reply_to_tweet_id = models.CharField(max_length=100, blank=True)
    quoted_tweet_id = models.CharField(max_length=100, blank=True)
    is_thread = models.BooleanField(default=False)
    thread_position = models.IntegerField(default=0)
    
    # Twitter-specific analytics
    retweets = models.IntegerField(default=0)
    quote_tweets = models.IntegerField(default=0)
    bookmarks = models.IntegerField(default=0)
    impressions = models.IntegerField(default=0)
    
    # X-Bot integration fields
    generated_tweet = models.OneToOneField('GeneratedTweet', null=True, blank=True, on_delete=models.SET_NULL)
    campaign_batch = models.ForeignKey('CampaignBatch', null=True, blank=True, on_delete=models.SET_NULL)
    brand_alignment_score = models.FloatField(null=True, blank=True)
    audience_target = models.CharField(max_length=50, null=True, blank=True)
    coophive_elements = models.JSONField(null=True, blank=True)
```

#### SourceTweet Model (n8n Integration)
```python
class SourceTweet(models.Model):
    """Source tweets from monitored accounts - for duplicate checking"""
    tweet_id = models.CharField(max_length=100, unique=True)
    url = models.URLField()
    content = models.TextField()
    likes = models.IntegerField(default=0)
    retweets = models.IntegerField(default=0)
    replies = models.IntegerField(default=0)
    quotes = models.IntegerField(default=0)
    views = models.IntegerField(default=0)
    date = models.DateTimeField()
    status = models.CharField(max_length=50, default="success")
    tweet_url = models.URLField()
    execution_id = models.CharField(max_length=255)
    source_url = models.CharField(max_length=255)
    processed_at = models.DateTimeField(auto_now_add=True)
    is_processed = models.BooleanField(default=False)
```

#### CampaignBatch Model (n8n Integration)
```python
class CampaignBatch(models.Model):
    """Campaign batches from n8n AI generation workflow"""
    batch_id = models.CharField(max_length=100, unique=True)
    analysis_summary = models.JSONField()
    total_tweets = models.IntegerField()
    ready_for_deployment = models.IntegerField()
    source_type = models.CharField(max_length=50, default="multi_agent_automation")
    title = models.CharField(max_length=255)
    description = models.TextField()
    brand_alignment_score = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default="Draft")
```

#### GeneratedTweet Model (n8n Integration)
```python
class GeneratedTweet(models.Model):
    """Individual generated tweets within a campaign batch"""
    STATUS_CHOICES = [
        ('Brand Aligned', 'Brand Aligned'),
        ('Draft', 'Draft'),
        ('Approved', 'Approved'),
        ('Posted', 'Posted'),
        ('Rejected', 'Rejected'),
        ('Deleted', 'Deleted'),
    ]
    
    campaign_batch = models.ForeignKey(CampaignBatch, on_delete=models.CASCADE, related_name='tweets')
    tweet_id = models.CharField(max_length=100)
    type = models.CharField(max_length=50)  # scientific_compute, infrastructure_optimization, etc.
    content = models.TextField()
    character_count = models.IntegerField()
    engagement_hook = models.TextField()
    coophive_elements = models.JSONField()  # Array of brand elements
    discord_voice_patterns = models.JSONField()  # Array of voice patterns
    theme_connection = models.TextField()
    ready_for_deployment = models.BooleanField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Brand Aligned")
    is_edited = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    published_at = models.DateTimeField(null=True, blank=True)
    x_com_post_id = models.CharField(max_length=100, null=True, blank=True)
```

### LinkedIn Models

#### LinkedInPost Model
```python
class LinkedInPost(Post):
    """LinkedIn-specific post model"""
    # LinkedIn-specific fields
    visibility = models.CharField(max_length=20, default='public')  # public, connections, logged-in
    article_url = models.URLField(blank=True)
    company_page_id = models.CharField(max_length=100, blank=True)
    
    # LinkedIn-specific analytics
    impressions = models.IntegerField(default=0)
    click_through_rate = models.FloatField(default=0.0)
    engagement_rate = models.FloatField(default=0.0)
```

### Farcaster Models

#### FarcasterPost Model
```python
class FarcasterPost(Post):
    """Farcaster-specific post model"""
    # Farcaster-specific fields
    cast_hash = models.CharField(max_length=100, blank=True)
    parent_cast_hash = models.CharField(max_length=100, blank=True)
    channel = models.CharField(max_length=100, blank=True)
    
    # Farcaster-specific analytics
    recasts = models.IntegerField(default=0)
    watches = models.IntegerField(default=0)
    reactions = models.JSONField(default=dict)  # Store different reaction types
```

### Bluesky Models

#### BlueskyPost Model
```python
class BlueskyPost(Post):
    """Bluesky-specific post model"""
    # Bluesky-specific fields
    rkey = models.CharField(max_length=100, blank=True)
    uri = models.CharField(max_length=255, blank=True)
    reply_root = models.CharField(max_length=255, blank=True)
    reply_parent = models.CharField(max_length=255, blank=True)
    
    # Bluesky-specific analytics
    reposts = models.IntegerField(default=0)
    self_labels = models.JSONField(default=list)  # Content labels/tags
```

## Database Relationships Diagram

```
# Authentication & Settings
User 1 ─┬─── * VerificationCode
        ├─── * AuthEvent
        └─── * (allauth SocialAccount)

AppSetting (standalone configuration storage)

# Core Content Management
Campaign 1 ─── * Post
Post 1 ─┬─── 1 TwitterPost (inheritance)
        ├─── 1 LinkedInPost (inheritance)
        ├─── 1 FarcasterPost (inheritance)
        └─── 1 BlueskyPost (inheritance)

MediaAsset (standalone file storage)

# Twitter n8n Integration
SourceTweet (standalone - source tweets from n8n)
CampaignBatch 1 ─── * GeneratedTweet
TwitterPost *─── 1 GeneratedTweet (optional)
TwitterPost *─── 1 CampaignBatch (optional)
```

## Key Model Relationships

### n8n Twitter Integration Flow
1. **SourceTweet**: Raw tweets from social listening (n8n → Django)
2. **CampaignBatch**: AI-generated campaign metadata (n8n → Django)  
3. **GeneratedTweet**: Individual AI-generated tweets (n8n → Django)
4. **TwitterPost**: Published posts (optional link to GeneratedTweet)

### Platform Inheritance
All platform posts inherit from the base `Post` model:
- **TwitterPost** extends Post with Twitter-specific fields
- **LinkedInPost** extends Post with LinkedIn-specific fields  
- **FarcasterPost** extends Post with Farcaster-specific fields
- **BlueskyPost** extends Post with Bluesky-specific fields

### Configuration Management
- **AppSetting**: Database-first configuration storage
- **SettingsManager**: Programmatic interface for settings

### Authentication System
- **User**: Django's built-in User model
- **VerificationCode**: Email verification and password reset codes
- **AuthEvent**: Comprehensive authentication audit logging

## Migrations

Each app maintains its own migrations in the `migrations/` directory:

```bash
# Generate new migrations
python manage.py makemigrations app_name

# Apply migrations
python manage.py migrate app_name

# Check migration status
python manage.py showmigrations

# Fake migrations (for schema matching)
python manage.py migrate --fake-initial
```

## Model Best Practices

1. **Always define `__str__` methods** for admin interface clarity
2. **Use appropriate field types** (CharField vs TextField, etc.)
3. **Add indexes for frequently queried fields** (tweet_id, batch_id, etc.)
4. **Use appropriate on_delete behavior** for ForeignKeys
5. **Keep models normalized** but allow denormalization for performance
6. **Use inheritance wisely** (Post → TwitterPost, etc.)
7. **Add comprehensive docstrings** for complex models
8. **Use JSONField for flexible metadata** (coophive_elements, reactions, etc.)
9. **Include created_at/updated_at timestamps** for audit trails
10. **Use choices for status fields** to maintain data integrity

## Database Schema Notes

### Twitter n8n Models
- **Unique constraints**: SourceTweet.tweet_id, CampaignBatch.batch_id
- **JSON fields**: Store complex AI-generated metadata flexibly
- **Foreign key relationships**: Enable campaign → tweets → posts flow

### Platform Extensibility
- **Inheritance pattern**: Easy to add new platforms by extending Post
- **Consistent analytics**: Common engagement metrics across platforms
- **Platform-specific fields**: Accommodate unique platform features

### Configuration Flexibility  
- **Database-first**: Runtime configuration changes without deployment
- **Environment fallback**: Bootstrap-friendly for initial setup
- **Type serialization**: Automatic JSON encoding/decoding for complex values

This model architecture supports both traditional social media management and advanced AI-powered content generation workflows while maintaining clean separation of concerns and platform extensibility.
