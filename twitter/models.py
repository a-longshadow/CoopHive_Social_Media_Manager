from django.db import models
from django.utils import timezone
from datetime import timedelta
from core.models import Post
import secrets

class SourceTweet(models.Model):
    """Source tweets from monitored accounts - for duplicate checking"""
    tweet_id = models.CharField(max_length=100, unique=True)  # Twitter's tweet ID
    url = models.URLField()
    content = models.TextField()
    likes = models.IntegerField(default=0)
    retweets = models.IntegerField(default=0)
    replies = models.IntegerField(default=0)
    quotes = models.IntegerField(default=0)
    views = models.IntegerField(default=0)
    date = models.DateTimeField()
    status = models.CharField(max_length=50, default="success")
    tweet_url = models.URLField()  # Full twitter.com URL
    execution_id = models.CharField(max_length=255)
    source_url = models.CharField(max_length=255)
    processed_at = models.DateTimeField(auto_now_add=True)
    is_processed = models.BooleanField(default=False)  # Used for AI generation

    class Meta:
        verbose_name = 'Source Tweet'
        verbose_name_plural = 'Source Tweets'
        ordering = ['-date']

    def __str__(self):
        return f"Tweet {self.tweet_id}: {self.content[:50]}..."

class CampaignBatch(models.Model):
    """Campaign batches from n8n AI generation workflow"""
    batch_id = models.CharField(max_length=100, unique=True)  # "batch_2025-08-12_15-07"
    secure_token = models.CharField(max_length=255, null=True, blank=True)  # Optional for Flask compatibility
    created_at = models.DateTimeField(auto_now_add=True)
    analysis_summary = models.JSONField()
    total_tweets = models.IntegerField()
    ready_for_deployment = models.IntegerField()
    source_type = models.CharField(max_length=50, default="multi_agent_automation")
    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=20, default="Draft")  # Draft, Reviewed, Published
    brand_alignment_score = models.FloatField(null=True, blank=True)

    class Meta:
        verbose_name = 'Campaign Batch'
        verbose_name_plural = 'Campaign Batches'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.batch_id} ({self.total_tweets} tweets)"

    def save(self, *args, **kwargs):
        if not self.secure_token:
            self.secure_token = secrets.token_urlsafe(32)
        super().save(*args, **kwargs)

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
    tweet_id = models.CharField(max_length=100)  # "batch_2025-07-31-tweet-1"
    type = models.CharField(max_length=50)  # "scientific_compute", etc.
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

    class Meta:
        verbose_name = 'Generated Tweet'
        verbose_name_plural = 'Generated Tweets'
        ordering = ['created_at']

    def __str__(self):
        return f"{self.tweet_id}: {self.content[:50]}..."

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
    generated_tweet = models.OneToOneField(GeneratedTweet, null=True, blank=True, on_delete=models.SET_NULL)
    campaign_batch = models.ForeignKey(CampaignBatch, null=True, blank=True, on_delete=models.SET_NULL)
    brand_alignment_score = models.FloatField(null=True, blank=True)
    audience_target = models.CharField(max_length=50, null=True, blank=True)
    coophive_elements = models.JSONField(null=True, blank=True)

    class Meta:
        verbose_name = 'Twitter Post'
        verbose_name_plural = 'Twitter Posts'
