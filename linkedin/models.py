from django.db import models
from core.models import Post

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

    class Meta:
        verbose_name = 'LinkedIn Post'
        verbose_name_plural = 'LinkedIn Posts'
