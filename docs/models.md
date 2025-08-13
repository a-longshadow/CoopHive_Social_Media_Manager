# Database Models Documentation

## Overview

This document details all database models across the application's Django apps.

## User Account Manager

### User Model
```python
class User(AbstractUser):
    email = models.EmailField(unique=True)
    email_verified = models.BooleanField(default=False)
    otp_enabled = models.BooleanField(default=False)
    otp_secret = models.CharField(max_length=32, blank=True)
    
    class Meta:
        db_table = 'auth_user'
        
    def verify_email(self):
        self.email_verified = True
        self.save()
```

### Profile Model
```python
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

## App Settings

### AppSetting Model
```python
class AppSetting(models.Model):
    key = models.CharField(max_length=100, unique=True, db_index=True)
    value = models.TextField(blank=True)
    description = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

## Platform Models

### Base Post Model
```python
class BasePost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    media_items = models.ManyToManyField('MediaItem', blank=True)
    schedule_time = models.DateTimeField(null=True, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('draft', 'Draft'),
            ('scheduled', 'Scheduled'),
            ('published', 'Published'),
            ('failed', 'Failed')
        ],
        default='draft'
    )
    
    class Meta:
        abstract = True
```

### MediaItem Model
```python
class MediaItem(models.Model):
    file = models.FileField(upload_to='media/')
    type = models.CharField(
        max_length=10,
        choices=[
            ('image', 'Image'),
            ('video', 'Video'),
            ('document', 'Document')
        ]
    )
    alt_text = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
```

### Platform-Specific Models

#### LinkedIn Post
```python
class LinkedInPost(BasePost):
    linkedin_post_id = models.CharField(max_length=100, null=True, blank=True)
    article_title = models.CharField(max_length=255, blank=True)
    article_url = models.URLField(blank=True)
```

#### Twitter Post
```python
class Tweet(BasePost):
    tweet_id = models.CharField(max_length=100, null=True, blank=True)
    in_reply_to = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)
    is_thread = models.BooleanField(default=False)
```

#### Farcaster Cast
```python
class Cast(BasePost):
    cast_id = models.CharField(max_length=100, null=True, blank=True)
    parent_hash = models.CharField(max_length=100, null=True, blank=True)
```

#### Bluesky Post
```python
class BlueskyPost(BasePost):
    post_id = models.CharField(max_length=100, null=True, blank=True)
    reply_to = models.CharField(max_length=100, null=True, blank=True)
```

## Analytics Models

### PostAnalytics
```python
class PostAnalytics(models.Model):
    post_id = models.CharField(max_length=100)
    platform = models.CharField(max_length=20)
    likes = models.IntegerField(default=0)
    shares = models.IntegerField(default=0)
    comments = models.IntegerField(default=0)
    impressions = models.IntegerField(default=0)
    engagement_rate = models.FloatField(default=0.0)
    collected_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['post_id', 'platform']),
            models.Index(fields=['collected_at'])
        ]
```

## Database Relationships Diagram

```
User 1 ─┬─── * LinkedInPost
        ├─── * Tweet
        ├─── * Cast
        ├─── * BlueskyPost
        └─── 1 Profile

BasePost *─── * MediaItem

PostAnalytics -> (post_id, platform)
```

## Migrations

Each app maintains its own migrations in the `migrations/` directory. To generate new migrations:

```bash
python manage.py makemigrations app_name
```

To apply migrations:

```bash
python manage.py migrate app_name
```

## Model Best Practices

1. Always define `__str__` methods
2. Use appropriate field types
3. Add indexes for frequently queried fields
4. Use appropriate on_delete behavior for ForeignKeys
5. Keep models normalized
6. Use abstract base classes for common fields
7. Add docstrings for complex models
