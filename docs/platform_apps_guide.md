# Platform Apps Guide

## Overview

CoopHive Social Media Manager supports four major social media platforms through dedicated Django apps. Each platform app provides specialized functionality while maintaining consistent patterns and shared infrastructure.

## Supported Platforms

- **Twitter/X.com**: Advanced n8n integration with AI-powered content generation
- **LinkedIn**: Professional networking with article and document support
- **Farcaster**: Decentralized social protocol with channel support
- **Bluesky**: Decentralized social network with AT Protocol integration

## Architecture Overview

### Common Patterns

All platform apps follow a consistent architecture:

```
platform_app/
├── models.py          # Platform-specific post models (inherit from core.Post)
├── views.py           # Platform-specific views and API endpoints
├── urls.py            # Platform-specific URL routing
├── admin.py           # Django admin configuration
├── apps.py            # App configuration
├── migrations/        # Database schema migrations
├── tests/             # Platform-specific tests
└── templates/
    └── platform_name/
        ├── dashboard.html    # Platform dashboard
        └── components/       # Reusable template components
```

### Shared Infrastructure

All platforms leverage:
- **Core Models**: Base `Post` and `Campaign` models
- **Authentication**: Unified user management system
- **Media Management**: Shared `MediaAsset` storage
- **Analytics**: Common engagement tracking patterns

## Twitter/X.com App

### Overview
The Twitter app is the most advanced platform integration, featuring:
- **n8n Workflow Integration**: Automated social listening and AI content generation
- **Scraped Tweets Database**: Management of source tweets from social listening
- **Campaign Review System**: Human oversight for AI-generated content
- **Advanced Analytics**: Comprehensive engagement tracking

### Key Features

#### n8n Integration
- **Duplicate Detection**: `/api/check-duplicate-tweet/` endpoint
- **Content Storage**: `/api/receive-tweets/` endpoint
- **Campaign Management**: AI-generated campaign batches
- **Review Workflow**: Human approval process for generated content

#### Models
```python
# Traditional Twitter posts
class TwitterPost(Post):
    reply_to_tweet_id = models.CharField(max_length=100, blank=True)
    quoted_tweet_id = models.CharField(max_length=100, blank=True)
    is_thread = models.BooleanField(default=False)
    thread_position = models.IntegerField(default=0)
    retweets = models.IntegerField(default=0)
    quote_tweets = models.IntegerField(default=0)
    bookmarks = models.IntegerField(default=0)
    impressions = models.IntegerField(default=0)

# n8n Integration models
class SourceTweet(models.Model):  # Raw tweets from social listening
class CampaignBatch(models.Model):  # AI-generated campaign metadata
class GeneratedTweet(models.Model):  # Individual AI-generated tweets
```

#### Key URLs
```python
urlpatterns = [
    # Dashboard and traditional management
    path('', views.dashboard, name='dashboard'),
    path('posts/', views.post_list, name='post_list'),
    
    # n8n Integration
    path('api/check-duplicate-tweet/', views.CheckDuplicateTweetAPIView.as_view()),
    path('api/receive-tweets/', views.ReceiveTweetsAPIView.as_view()),
    
    # Scraped tweets management
    path('sourcetweet/', views.ScrapedTweetsView.as_view(), name='scraped_tweets'),
    
    # Campaign review system
    path('generate-tweets/', views.GenerateTweetsView.as_view()),
    path('review/<str:campaign_batch>/', views.CampaignReviewView.as_view()),
    
    # Tweet management APIs
    path('api/save-generated-tweet/<int:tweet_id>/', views.SaveGeneratedTweetAPIView.as_view()),
    path('api/approve-generated-tweet/<int:tweet_id>/', views.ApproveGeneratedTweetAPIView.as_view()),
]
```

#### Dashboard Features
- **Source Tweets Database**: Modern interface for managing scraped tweets
- **Campaign Management**: Review and approve AI-generated content
- **Analytics Dashboard**: Engagement metrics and performance tracking
- **Bulk Operations**: Mass actions for tweet management

### Usage Examples

#### Traditional Tweet Creation
```python
from twitter.models import TwitterPost
from core.models import Campaign

campaign = Campaign.objects.create(
    name="Product Launch",
    platform="twitter"
)

tweet = TwitterPost.objects.create(
    campaign=campaign,
    content="Exciting product launch coming soon! #innovation #tech",
    status="draft",
    platform="twitter"
)
```

#### n8n Integration
```bash
# Test duplicate check
curl -X POST http://localhost:8000/twitter/api/check-duplicate-tweet/ \
  -H "Content-Type: application/json" \
  -d '{"execution_id": "test", "tweets": [...]}'

# Test campaign receipt
curl -X POST http://localhost:8000/twitter/api/receive-tweets/ \
  -H "Content-Type: application/json" \
  -d '[{"campaign_batch": "test_batch", "tweets": [...]}]'
```

## LinkedIn App

### Overview
LinkedIn integration focuses on professional networking with support for:
- **Standard Posts**: Text and media posts
- **Article Posts**: Link sharing with article metadata
- **Document Posts**: Professional document sharing
- **Company Page Management**: Corporate account posting

### Key Features

#### Models
```python
class LinkedInPost(Post):
    visibility = models.CharField(max_length=20, default='public')  # public, connections, logged-in
    article_url = models.URLField(blank=True)
    company_page_id = models.CharField(max_length=100, blank=True)
    impressions = models.IntegerField(default=0)
    click_through_rate = models.FloatField(default=0.0)
    engagement_rate = models.FloatField(default=0.0)
```

#### URLs
```python
urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('posts/', views.post_list, name='post_list'),
    path('posts/new/', views.post_create, name='post_create'),
    
    # Specialized post types
    path('articles/new/', views.article_post_create, name='article_post_create'),
    path('documents/new/', views.document_post_create, name='document_post_create'),
    
    # API endpoints
    path('api/preview/', views.generate_preview, name='generate_preview'),
    path('api/schedule/', views.schedule_post, name='schedule_post'),
    path('api/publish/', views.publish_post, name='publish_post'),
    
    # Analytics
    path('analytics/', views.analytics, name='analytics'),
    path('analytics/export/', views.export_analytics, name='export_analytics'),
]
```

#### Dashboard Features
- **Post Creation Wizard**: Step-by-step post creation
- **Article Integration**: Link preview and metadata extraction
- **Document Management**: Professional document sharing
- **Visibility Controls**: Public, connections, or logged-in users
- **Company Page Support**: Multi-account management

### Usage Examples

#### Standard LinkedIn Post
```python
from linkedin.models import LinkedInPost

post = LinkedInPost.objects.create(
    content="Excited to share our latest insights on industry trends...",
    visibility="public",
    status="draft",
    platform="linkedin"
)
```

#### Article Post
```python
article_post = LinkedInPost.objects.create(
    content="Check out our latest article on digital transformation...",
    article_url="https://company.com/blog/digital-transformation",
    visibility="public",
    post_type="article"
)
```

#### Document Post
```python
document_post = LinkedInPost.objects.create(
    content="Our Q3 industry report is now available...",
    document_title="Q3 Industry Report 2025",
    visibility="connections",
    post_type="document"
)
```

## Farcaster App

### Overview
Farcaster integration supports the decentralized social protocol with:
- **Cast Management**: Farcaster's equivalent of tweets
- **Channel Support**: Topic-based communities
- **Reaction Tracking**: Various reaction types beyond simple likes
- **Decentralized Identity**: Integration with Farcaster's identity system

### Key Features

#### Models
```python
class FarcasterPost(Post):
    cast_hash = models.CharField(max_length=100, blank=True)
    parent_cast_hash = models.CharField(max_length=100, blank=True)  # For replies
    channel = models.CharField(max_length=100, blank=True)
    recasts = models.IntegerField(default=0)
    watches = models.IntegerField(default=0)
    reactions = models.JSONField(default=dict)  # Multiple reaction types
```

#### URLs
```python
urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('casts/', views.cast_list, name='cast_list'),
    path('casts/new/', views.cast_create, name='cast_create'),
    path('channels/', views.channel_list, name='channel_list'),
    
    # API endpoints
    path('api/cast/', views.create_cast, name='create_cast'),
    path('api/recast/', views.recast, name='recast'),
    path('api/react/', views.add_reaction, name='add_reaction'),
    
    # Analytics
    path('analytics/', views.analytics, name='analytics'),
]
```

#### Dashboard Features
- **Cast Composer**: Rich text cast creation
- **Channel Browser**: Discover and join channels
- **Reaction Analytics**: Track different reaction types
- **Thread Management**: Reply and conversation tracking
- **Decentralized Features**: Farcaster protocol integration

### Usage Examples

#### Standard Cast
```python
from farcaster.models import FarcasterPost

cast = FarcasterPost.objects.create(
    content="Building the future of decentralized social media 🚀",
    channel="coophive",
    status="published",
    platform="farcaster"
)
```

#### Reply Cast
```python
reply_cast = FarcasterPost.objects.create(
    content="Totally agree! The potential is huge.",
    parent_cast_hash="0x1234567890abcdef",
    channel="coophive",
    status="published"
)
```

#### Channel-Specific Cast
```python
channel_cast = FarcasterPost.objects.create(
    content="Weekly update on our decentralized computing progress...",
    channel="web3-builders",
    status="scheduled",
    scheduled_time=timezone.now() + timedelta(hours=2)
)
```

## Bluesky App

### Overview
Bluesky integration supports the AT Protocol with:
- **Post Management**: Text and media posts
- **Reply Threading**: Conversation tracking
- **Content Labels**: Self-labeling system
- **Decentralized Identity**: AT Protocol DIDs

### Key Features

#### Models
```python
class BlueskyPost(Post):
    rkey = models.CharField(max_length=100, blank=True)  # Record key
    uri = models.CharField(max_length=255, blank=True)  # AT Protocol URI
    reply_root = models.CharField(max_length=255, blank=True)  # Thread root
    reply_parent = models.CharField(max_length=255, blank=True)  # Direct parent
    reposts = models.IntegerField(default=0)
    self_labels = models.JSONField(default=list)  # Content labels
```

#### URLs
```python
urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('posts/', views.post_list, name='post_list'),
    path('posts/new/', views.post_create, name='post_create'),
    path('threads/', views.thread_list, name='thread_list'),
    
    # API endpoints
    path('api/post/', views.create_post, name='create_post'),
    path('api/repost/', views.repost, name='repost'),
    path('api/follow/', views.follow_user, name='follow_user'),
    
    # Analytics
    path('analytics/', views.analytics, name='analytics'),
]
```

#### Dashboard Features
- **Post Composer**: Rich media post creation
- **Thread Viewer**: Conversation navigation
- **Label Management**: Content self-labeling
- **Following Management**: User relationship tracking
- **AT Protocol Integration**: Decentralized identity features

### Usage Examples

#### Standard Bluesky Post
```python
from bluesky.models import BlueskyPost

post = BlueskyPost.objects.create(
    content="Exploring the potential of decentralized social networks...",
    self_labels=["tech", "web3"],
    status="published",
    platform="bluesky"
)
```

#### Reply Post
```python
reply_post = BlueskyPost.objects.create(
    content="Great point about decentralization benefits!",
    reply_root="at://did:plc:123.../app.bsky.feed.post/456",
    reply_parent="at://did:plc:123.../app.bsky.feed.post/456",
    status="published"
)
```

#### Labeled Content Post
```python
labeled_post = BlueskyPost.objects.create(
    content="Technical deep-dive into AT Protocol architecture...",
    self_labels=["technical", "long-form", "architecture"],
    status="draft"
)
```

## Cross-Platform Features

### Unified Campaign Management

#### Multi-Platform Campaigns
```python
from core.models import Campaign
from twitter.models import TwitterPost
from linkedin.models import LinkedInPost

# Create a cross-platform campaign
campaign = Campaign.objects.create(
    name="Product Launch 2025",
    description="Multi-platform product announcement",
    platform="multi"  # Special designation for cross-platform
)

# Create platform-specific posts for the same campaign
twitter_post = TwitterPost.objects.create(
    campaign=campaign,
    content="🚀 Excited to announce our latest innovation! #ProductLaunch",
    platform="twitter"
)

linkedin_post = LinkedInPost.objects.create(
    campaign=campaign,
    content="We're thrilled to introduce our latest product innovation...",
    visibility="public",
    platform="linkedin"
)
```

#### Campaign Analytics
```python
def get_campaign_analytics(campaign_id):
    campaign = Campaign.objects.get(id=campaign_id)
    
    # Aggregate analytics across all platforms
    total_engagement = 0
    platform_breakdown = {}
    
    for post in campaign.post_set.all():
        engagement = post.likes + post.shares + post.comments
        total_engagement += engagement
        
        if post.platform not in platform_breakdown:
            platform_breakdown[post.platform] = 0
        platform_breakdown[post.platform] += engagement
    
    return {
        'campaign': campaign,
        'total_engagement': total_engagement,
        'platform_breakdown': platform_breakdown
    }
```

### Shared Media Management

#### Media Asset Integration
```python
from core.models import MediaAsset

# Upload media for cross-platform use
media_asset = MediaAsset.objects.create(
    file_path="/media/uploads/product-image.jpg",
    file_type="image/jpeg",
    file_size=1024000
)

# Use same media across platforms
twitter_post = TwitterPost.objects.create(
    content="Check out our new product! 🔥",
    media_urls=f"/media/{media_asset.file_path}"
)

linkedin_post = LinkedInPost.objects.create(
    content="Introducing our latest innovation...",
    media_urls=f"/media/{media_asset.file_path}"
)
```

### Consistent API Patterns

All platforms follow consistent API patterns:

#### Standard CRUD Operations
```http
GET /platform/posts/          # List posts
POST /platform/posts/         # Create post
GET /platform/posts/{id}/     # Get specific post
PUT /platform/posts/{id}/     # Update post
DELETE /platform/posts/{id}/  # Delete post
```

#### Publishing Operations
```http
POST /platform/api/publish/   # Publish post immediately
POST /platform/api/schedule/  # Schedule post for later
POST /platform/api/preview/   # Generate post preview
```

#### Analytics Operations
```http
GET /platform/analytics/              # Platform analytics dashboard
GET /platform/analytics/export/      # Export analytics data
GET /platform/api/engagement/{id}/   # Get post engagement metrics
```

## Development Guidelines

### Adding New Platforms

To add a new platform, follow these steps:

1. **Create Django App**:
```bash
python manage.py startapp new_platform
```

2. **Create Platform Model**:
```python
# new_platform/models.py
from core.models import Post

class NewPlatformPost(Post):
    # Platform-specific fields
    platform_post_id = models.CharField(max_length=100, blank=True)
    platform_specific_field = models.CharField(max_length=200)
    
    # Platform-specific analytics
    platform_metric = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = 'New Platform Post'
        verbose_name_plural = 'New Platform Posts'
```

3. **Create Views and URLs**:
```python
# new_platform/views.py
def dashboard(request):
    return render(request, 'new_platform/dashboard.html')

# new_platform/urls.py
from django.urls import path
from . import views

app_name = 'new_platform'
urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    # Add other URL patterns following the standard pattern
]
```

4. **Add to Main URLs**:
```python
# coophive/urls.py
urlpatterns = [
    # ... existing patterns
    path('new-platform/', include('new_platform.urls')),
]
```

5. **Update Settings**:
```python
# coophive/settings.py
INSTALLED_APPS = [
    # ... existing apps
    'new_platform.apps.NewPlatformConfig',
]
```

### Testing Patterns

Each platform app should include comprehensive tests:

```python
# platform/tests/test_models.py
from django.test import TestCase
from platform.models import PlatformPost
from core.models import Campaign

class PlatformPostModelTests(TestCase):
    def setUp(self):
        self.campaign = Campaign.objects.create(
            name="Test Campaign",
            platform="platform"
        )
    
    def test_post_creation(self):
        post = PlatformPost.objects.create(
            campaign=self.campaign,
            content="Test content",
            status="draft"
        )
        self.assertEqual(post.content, "Test content")
        self.assertEqual(post.platform, "platform")
```

### Best Practices

1. **Model Inheritance**: Always inherit from `core.models.Post` for consistency
2. **URL Naming**: Use consistent URL patterns across platforms
3. **Template Structure**: Follow the established template organization
4. **API Consistency**: Maintain consistent API response formats
5. **Error Handling**: Implement comprehensive error handling
6. **Documentation**: Document platform-specific features thoroughly
7. **Testing**: Write comprehensive tests for all functionality

## Platform-Specific Considerations

### Twitter/X.com
- **Rate Limits**: Respect X.com API rate limits
- **Character Limits**: 280 characters for standard tweets
- **Media Handling**: Images, videos, and GIFs support
- **Thread Support**: Multi-tweet thread management

### LinkedIn
- **Professional Tone**: Content should maintain professional standards
- **Article Integration**: Rich link previews and metadata
- **Company Pages**: Support for corporate account management
- **Document Sharing**: Professional document distribution

### Farcaster
- **Decentralized Protocol**: Integration with Farcaster hubs
- **Channel System**: Topic-based community engagement
- **Reaction Diversity**: Support for multiple reaction types
- **Identity Management**: Farcaster ID and verification

### Bluesky
- **AT Protocol**: Integration with decentralized identity
- **Content Labels**: Self-labeling and moderation system
- **Threading**: Rich conversation and reply management
- **Decentralized Features**: DID-based identity and content addressing

This platform architecture provides a solid foundation for multi-platform social media management while allowing for platform-specific features and optimizations.
