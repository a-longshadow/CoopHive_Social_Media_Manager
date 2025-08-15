from django.db import models
from django.contrib.auth.models import User


class Campaign(models.Model):
    """Campaign model for organizing posts"""
    name = models.CharField(max_length=200)
    platform = models.CharField(max_length=50)
    status = models.CharField(max_length=20)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    total_posts = models.IntegerField(default=0)
    total_engagement = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.platform})"

class Post(models.Model):
    """Base post model for social media platforms"""
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
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.platform}: {self.content[:50]}..."

class MediaAsset(models.Model):
    """Media assets for posts"""
    file_path = models.CharField(max_length=500, blank=True, default='')
    file_type = models.CharField(max_length=50)
    file_size = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.file_type}: {self.file_path}"
