from django.contrib import admin
from .models import TwitterPost

@admin.register(TwitterPost)
class TwitterPostAdmin(admin.ModelAdmin):
    list_display = ('campaign', 'status', 'is_thread', 'thread_position', 'retweets', 'likes', 'scheduled_time')
    list_filter = ('status', 'is_thread')
    search_fields = ('content', 'campaign__name', 'reply_to_tweet_id')
    readonly_fields = ('retweets', 'quote_tweets', 'likes', 'bookmarks', 'impressions')
