from django.db import models
from core.models import Post

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

    class Meta:
        verbose_name = 'Twitter Post'
        verbose_name_plural = 'Twitter Posts'
