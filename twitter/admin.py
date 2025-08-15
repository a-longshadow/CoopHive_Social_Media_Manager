from django.contrib import admin
from .models import TwitterPost, SourceTweet, CampaignBatch, GeneratedTweet

@admin.register(SourceTweet)
class SourceTweetAdmin(admin.ModelAdmin):
    list_display = ('tweet_id', 'content_preview', 'likes', 'retweets', 'date', 'is_processed')
    list_filter = ('is_processed', 'status', 'date')
    search_fields = ('tweet_id', 'content', 'execution_id')
    readonly_fields = ('processed_at',)
    
    def content_preview(self, obj):
        return obj.content[:100] + "..." if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'Content'

@admin.register(CampaignBatch)
class CampaignBatchAdmin(admin.ModelAdmin):
    list_display = ('batch_id', 'title', 'total_tweets', 'status', 'brand_alignment_score', 'created_at')
    list_filter = ('status', 'source_type', 'created_at')
    search_fields = ('batch_id', 'title', 'description')
    readonly_fields = ('created_at', 'secure_token')

@admin.register(GeneratedTweet)
class GeneratedTweetAdmin(admin.ModelAdmin):
    list_display = ('tweet_id', 'campaign_batch', 'content_preview', 'status', 'character_count', 'ready_for_deployment')
    list_filter = ('status', 'ready_for_deployment', 'is_edited', 'type')
    search_fields = ('tweet_id', 'content', 'campaign_batch__batch_id')
    readonly_fields = ('created_at', 'published_at')
    
    def content_preview(self, obj):
        return obj.content[:100] + "..." if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'Content'

@admin.register(TwitterPost)
class TwitterPostAdmin(admin.ModelAdmin):
    list_display = ('content_preview', 'status', 'is_thread', 'thread_position', 'retweets', 'likes', 'scheduled_time')
    list_filter = ('status', 'is_thread', 'created_at')
    search_fields = ('content', 'reply_to_tweet_id', 'platform_post_id')
    readonly_fields = ('retweets', 'quote_tweets', 'bookmarks', 'impressions', 'created_at', 'updated_at', 'published_time')
    
    def content_preview(self, obj):
        return obj.content[:100] + "..." if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'Content'
