from django.urls import path
from . import views

app_name = 'twitter'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # SCRAPED TWEETS DATABASE INTERFACE (matches X-Bot production)
    path('sourcetweet/', views.ScrapedTweetsView.as_view(), name='scraped_tweets'),
    path('scraped-tweets/', views.ScrapedTweetsView.as_view(), name='scraped_tweets_alt'),
    path('sourcetweet/export/', views.ExportTweetsView.as_view(), name='export_tweets'),
    
    # FLASK API COMPATIBILITY - CRITICAL FOR N8N INTEGRATION
    path('api/check-duplicate-tweet/', views.CheckDuplicateTweetAPIView.as_view(), name='api_check_duplicate'),
    path('api/receive-tweets/', views.ReceiveTweetsAPIView.as_view(), name='api_receive_tweets'),
    
    # AJAX API ENDPOINTS FOR FRONTEND INTERACTIONS
    path('api/tweet-details/<int:tweet_id>/', views.TweetDetailAPIView.as_view(), name='api_tweet_details'),
    path('api/delete-tweet/<int:tweet_id>/', views.DeleteTweetAPIView.as_view(), name='api_delete_tweet'),
    path('api/bulk-delete-tweets/', views.BulkDeleteTweetsAPIView.as_view(), name='api_bulk_delete_tweets'),
    
    # GENERATED TWEET ACTION ENDPOINTS
    path('api/save-generated-tweet/<int:tweet_id>/', views.SaveGeneratedTweetAPIView.as_view(), name='api_save_generated_tweet'),
    path('api/approve-generated-tweet/<int:tweet_id>/', views.ApproveGeneratedTweetAPIView.as_view(), name='api_approve_generated_tweet'),
    path('api/reject-generated-tweet/<int:tweet_id>/', views.RejectGeneratedTweetAPIView.as_view(), name='api_reject_generated_tweet'),
    path('api/delete-generated-tweet/<int:tweet_id>/', views.DeleteGeneratedTweetAPIView.as_view(), name='api_delete_generated_tweet'),
    path('api/post-tweet-to-x/<int:tweet_id>/', views.PostTweetToXAPIView.as_view(), name='api_post_tweet_to_x'),
    
    # MAIN INTERFACES (matches Flask app URLs)
    path('generate-tweets/', views.GenerateTweetsView.as_view(), name='generate_tweets'),
    path('review/<str:campaign_batch>/', views.CampaignReviewView.as_view(), name='campaign_review'),
    
    # Posts
    path('posts/', views.post_list, name='post_list'),
    path('posts/new/', views.post_create, name='post_create'),
    path('posts/<int:pk>/', views.post_detail, name='post_detail'),
    path('posts/<int:pk>/edit/', views.post_edit, name='post_edit'),
    path('posts/<int:pk>/delete/', views.post_delete, name='post_delete'),
    
    # Media handling
    path('media/upload/', views.media_upload, name='media_upload'),
    path('media/<int:pk>/delete/', views.media_delete, name='media_delete'),
    
    # API endpoints
    path('api/preview/', views.generate_preview, name='generate_preview'),
    path('api/schedule/', views.schedule_tweet, name='schedule_tweet'),
    path('api/post/', views.post_tweet, name='post_tweet'),
    
    # Analytics
    path('analytics/', views.analytics, name='analytics'),
    path('analytics/export/', views.export_analytics, name='export_analytics'),
]
