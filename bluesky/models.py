from django.db import models
from core.models import Post

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
    
    class Meta:
        verbose_name = 'Bluesky Post'
        verbose_name_plural = 'Bluesky Posts'
