from django.db import models
from django.utils import timezone

class Campaign(models.Model):
    """Base campaign model for all social media platforms"""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Campaign metadata
    platform = models.CharField(max_length=50)  # linkedin, twitter, farcaster, bluesky
    status = models.CharField(max_length=20, default='draft')  # draft, active, completed, paused
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    
    # Analytics
    total_posts = models.IntegerField(default=0)
    total_engagement = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.platform})"

class Post(models.Model):
    """Base post model for all social media content"""
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Post metadata
    platform = models.CharField(max_length=50)
    status = models.CharField(max_length=20, default='draft')  # draft, scheduled, published, failed
    scheduled_time = models.DateTimeField(null=True, blank=True)
    published_time = models.DateTimeField(null=True, blank=True)
    
    # Platform-specific IDs
    platform_post_id = models.CharField(max_length=100, blank=True)
    
    # Analytics
    likes = models.IntegerField(default=0)
    shares = models.IntegerField(default=0)
    comments = models.IntegerField(default=0)
    views = models.IntegerField(default=0)
    
    # Content optimization
    hashtags = models.JSONField(default=list, blank=True)
    mentions = models.JSONField(default=list, blank=True)
    media_urls = models.JSONField(default=list, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.platform} post - {self.campaign.name}"

class MediaAsset(models.Model):
    """Model for managing media files across platforms"""
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='media_assets')
    file_type = models.CharField(max_length=20)  # image, video, gif
    file_url = models.URLField()
    original_filename = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=timezone.now)
    
    # Platform-specific media IDs
    platform_media_ids = models.JSONField(default=dict)
    
    class Meta:
        ordering = ['created_at']
        
    def __str__(self):
        return f"{self.file_type} - {self.original_filename}"
