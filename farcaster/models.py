from django.db import models
from core.models import Post

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
    
    class Meta:
        verbose_name = 'Farcaster Post'
        verbose_name_plural = 'Farcaster Posts'
