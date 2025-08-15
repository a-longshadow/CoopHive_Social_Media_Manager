# Twitter/X-Bot Integration Guide

## Overview

This comprehensive guide covers the complete integration between the CoopHive Social Media Manager and the X-Bot n8n workflow system. The integration enables automated social listening, AI-powered content generation, and streamlined content management.

## System Architecture

### Complete Data Flow
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────────┐
│   n8n Workflow │    │  Django Twitter  │    │   Review Interface  │
│   (X-Bot 24)    │    │      App         │    │                     │
└─────────────────┘    └──────────────────┘    └─────────────────────┘
         │                        │                        │
         │ 1. Source Tweets       │                        │
         │ ─────────────────────► │                        │
         │    (check duplicates)  │                        │
         │                        │                        │
         │ 2. Filtered Tweets     │                        │
         │ ◄───────────────────── │                        │
         │    (new tweets only)   │                        │
         │                        │                        │
         │ 3. AI Processing       │                        │
         │ (brand alignment)      │                        │
         │                        │                        │
         │ 4. Generated Content   │                        │
         │ ─────────────────────► │                        │
         │    (campaign batch)    │                        │
         │                        │                        │
         │                        │ 5. Review & Approval   │
         │                        │ ─────────────────────► │
         │                        │                        │
         │                        │ 6. Publishing          │
         │                        │ ◄───────────────────── │
```

### Key Components

1. **n8n Workflow** (`X_Bot (24).json`): Social listening and AI content generation
2. **Django API Endpoints**: Data ingestion and storage
3. **Database Models**: Structured data storage
4. **Review Interface**: Human oversight and approval
5. **Publishing System**: Content distribution to X.com

## Phase 1: Source Tweet Ingestion

### n8n → Django Flow

#### 1.1 Duplicate Check Endpoint
**URL**: `/twitter/api/check-duplicate-tweet/`

**Purpose**: Primary endpoint that n8n hits to check for duplicate tweets and store new ones.

**n8n Configuration**:
```json
{
  "method": "POST",
  "url": "http://127.0.0.1:8000/twitter/api/check-duplicate-tweet/",
  "sendHeaders": true,
  "headerParameters": {
    "parameters": [
      {
        "name": "Content-Type",
        "value": "application/json"
      }
    ]
  },
  "sendBody": true,
  "specifyBody": "json",
  "jsonBody": "={{ JSON.stringify($json) }}"
}
```

**Input Format** (from n8n):
```json
{
  "execution_id": "exec_2025-08-14_1607_n8n_r26hp94b",
  "source_url": "https://n8n.coophive.network",
  "tweets": [
    {
      "Tweet ID": "1956000485229441027",
      "URL": "https://x.com/user/status/1956000485229441027",
      "Content": "Tweet content...",
      "Likes": 0,
      "Retweets": 0,
      "Replies": 0,
      "Quotes": 0,
      "Views": 593,
      "Date": "Thu Aug 14 14:30:31 +0000 2025",
      "Status": "success",
      "Tweet": "https://twitter.com/user/status/1956000485229441027"
    }
  ],
  "batch_metadata": {
    "total_tweets": 3,
    "processing_timestamp": "2025-08-14T16:07:32.837Z",
    "accounts_processed": 6
  }
}
```

**Response Format** (to n8n):
```json
{
  "data": {
    "duplicate_ids": [],
    "execution_id": "exec_2025-08-14_1607_n8n_r26hp94b",
    "new_tweets": [
      {
        "Content": "Tweet content...",
        "Date": "Thu Aug 14 14:30:31 +0000 2025",
        "Likes": 0,
        "Tweet ID": "1956000485229441027",
        "URL": "https://x.com/user/status/1956000485229441027",
        "Views": 593
      }
    ],
    "source_url": "https://n8n.coophive.network"
  },
  "status": "success",
  "summary": {
    "duplicates_found": 0,
    "new_tweets_found": 3,
    "total_processed": 3
  }
}
```

#### 1.2 Database Storage
New tweets are stored in the `SourceTweet` model:

```python
class SourceTweet(models.Model):
    tweet_id = models.CharField(max_length=100, unique=True)
    url = models.URLField()
    content = models.TextField()
    likes = models.IntegerField(default=0)
    retweets = models.IntegerField(default=0)
    replies = models.IntegerField(default=0)
    quotes = models.IntegerField(default=0)
    views = models.IntegerField(default=0)
    date = models.DateTimeField()
    execution_id = models.CharField(max_length=255)
    source_url = models.CharField(max_length=255)
    processed_at = models.DateTimeField(auto_now_add=True)
```

#### 1.3 Duplicate Detection Logic
- **Primary Key**: `tweet_id` (unique constraint)
- **Atomic Operations**: All database operations wrapped in transactions
- **Logging**: Comprehensive logging for debugging and monitoring

## Phase 2: AI Content Generation

### n8n AI Processing

After receiving filtered tweets, n8n processes them through AI agents:

1. **Sentiment Analysis**: Analyzes tweet sentiment and engagement factors
2. **Twitter Expert Agent**: Creates initial tweet variations
3. **Brand Expert Agent**: Aligns content with CoopHive's "Cyber Architect" voice
4. **Multi-Agent Output**: Final brand-aligned tweets ready for review

### Generated Content Storage

#### 2.1 Receive Generated Tweets Endpoint
**URL**: `/twitter/api/receive-tweets/`

**Purpose**: Stores AI-generated campaign batches from n8n workflow.

**Input Format** (from n8n):
```json
[{
  "campaign_batch": "batch_2025-08-14_16-10",
  "generated_at": "2025-08-14T16:10:46.172Z",
  "analysis_summary": {
    "input_batch_size": 3,
    "dominant_themes": ["brand_alignment", "cyber_architect", "agent_first"],
    "brand_alignment_score": 9,
    "content_strategy": "Multi-agent brand alignment with Cyber Architect voice"
  },
  "tweets": [
    {
      "id": "batch_2025-08-14_16-10-tweet-1",
      "type": "scientific_compute",
      "content": "Architecting research workflows: CoopHive designs the rails for immediate compute access. Blueprint your discoveries, execute without delay. #DecentralizedCompute",
      "character_count": 218,
      "engagement_hook": "Compute Without Queues",
      "coophive_elements": ["agent-first", "compute-orchestration", "queue-elimination"],
      "discord_voice_patterns": ["blueprint-precision", "architectural-clarity"],
      "theme_connection": "Refined tweets to fully embody the Cyber Architect persona",
      "ready_for_deployment": true,
      "status": "Brand Aligned",
      "is_edited": false
    }
  ],
  "tweet_count": 3,
  "title": "Multi-Agent Brand-Aligned Content",
  "description": "AI-generated tweets optimized for CoopHive brand voice",
  "source_type": "multi_agent_automation"
}]
```

**Response Format** (to n8n):
```json
[{
  "campaign_batch": "batch_2025-08-14_16-10",
  "message": "Received 3 tweets (saved to database)",
  "status": "success"
}]
```

#### 2.2 Database Models for Generated Content

**CampaignBatch Model**:
```python
class CampaignBatch(models.Model):
    batch_id = models.CharField(max_length=100, unique=True)
    analysis_summary = models.JSONField()
    total_tweets = models.IntegerField()
    ready_for_deployment = models.IntegerField()
    brand_alignment_score = models.FloatField(null=True, blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default="Draft")
```

**GeneratedTweet Model**:
```python
class GeneratedTweet(models.Model):
    campaign_batch = models.ForeignKey(CampaignBatch, on_delete=models.CASCADE)
    tweet_id = models.CharField(max_length=100)
    type = models.CharField(max_length=50)  # scientific_compute, infrastructure_optimization, etc.
    content = models.TextField()
    character_count = models.IntegerField()
    engagement_hook = models.TextField()
    coophive_elements = models.JSONField()  # Brand elements
    discord_voice_patterns = models.JSONField()  # Voice patterns
    theme_connection = models.TextField()
    ready_for_deployment = models.BooleanField()
    status = models.CharField(max_length=20, default="Brand Aligned")
    is_edited = models.BooleanField(default=False)
```

## Phase 3: Content Review and Management

### Review Interface

#### 3.1 Campaign Dashboard
**URL**: `/twitter/generate-tweets/`

**Features**:
- List all campaign batches with status badges
- Show batch metadata (date, tweet count, brand alignment scores)
- Campaign overview statistics
- Quick access to review interfaces

#### 3.2 Campaign Review Interface
**URL**: `/twitter/review/{campaign_batch}/`

**Features**:
- Campaign overview with statistics
- Individual tweet cards with full editing capability
- Action buttons per tweet: Save, Approve, Reject, Delete, Post to X.com
- Bulk actions: Approve All, Save All Changes
- Real-time character counting and validation

#### 3.3 Tweet Management APIs

**Save Generated Tweet**:
```http
POST /twitter/api/save-generated-tweet/{tweet_id}/
Content-Type: application/json

{
  "content": "Updated tweet content..."
}
```

**Approve Generated Tweet**:
```http
POST /twitter/api/approve-generated-tweet/{tweet_id}/
```

**Reject Generated Tweet**:
```http
POST /twitter/api/reject-generated-tweet/{tweet_id}/
```

**Delete Generated Tweet**:
```http
DELETE /twitter/api/delete-generated-tweet/{tweet_id}/
```

**Post Tweet to X.com**:
```http
POST /twitter/api/post-tweet-to-x/{tweet_id}/
```

### Status Management

Generated tweets progress through these statuses:
1. **Brand Aligned**: Initial AI-generated state
2. **Draft**: Edited by human reviewer
3. **Approved**: Ready for publishing
4. **Posted**: Successfully published to X.com
5. **Rejected**: Not suitable for publishing
6. **Deleted**: Removed from campaign

## Phase 4: Scraped Tweets Database

### Source Tweet Management

#### 4.1 Scraped Tweets Interface
**URL**: `/twitter/sourcetweet/`

**Features**:
- Modern glassmorphism design with responsive layout
- Advanced search and filtering capabilities
- Sortable columns with engagement metrics
- Bulk operations (delete, export)
- Tweet detail modals with full metadata

#### 4.2 Source Tweet APIs

**Get Tweet Details**:
```http
GET /twitter/api/tweet-details/{tweet_id}/
```

**Delete Single Tweet**:
```http
DELETE /twitter/api/delete-tweet/{tweet_id}/
```

**Bulk Delete Tweets**:
```http
POST /twitter/api/bulk-delete-tweets/
Content-Type: application/json

{
  "tweet_ids": [1, 2, 3, 4, 5]
}
```

**Export Tweets**:
```http
GET /twitter/sourcetweet/export/?format=csv
```

#### 4.3 Search and Filtering

**Advanced Search Features**:
- Content text search
- Tweet ID search
- Author/URL filtering
- Date range filtering
- Engagement threshold filtering
- Execution ID filtering

**Sortable Columns**:
- Date (ascending/descending)
- Engagement metrics (likes, retweets, views)
- Content length
- Processing status

## Phase 5: Integration Setup and Configuration

### 5.1 Django Setup

**Required Models Migration**:
```bash
# Apply Twitter app migrations
python manage.py migrate twitter

# Verify models are created
python manage.py shell -c "
from twitter.models import SourceTweet, CampaignBatch, GeneratedTweet
print(f'Models ready: {SourceTweet._meta.db_table}, {CampaignBatch._meta.db_table}, {GeneratedTweet._meta.db_table}')
"
```

**URL Configuration**:
```python
# twitter/urls.py
urlpatterns = [
    # n8n Integration Endpoints
    path('api/check-duplicate-tweet/', views.CheckDuplicateTweetAPIView.as_view(), name='api_check_duplicate'),
    path('api/receive-tweets/', views.ReceiveTweetsAPIView.as_view(), name='api_receive_tweets'),
    
    # Review Interface
    path('generate-tweets/', views.GenerateTweetsView.as_view(), name='generate_tweets'),
    path('review/<str:campaign_batch>/', views.CampaignReviewView.as_view(), name='campaign_review'),
    
    # Scraped Tweets Interface
    path('sourcetweet/', views.ScrapedTweetsView.as_view(), name='scraped_tweets'),
    
    # Management APIs
    path('api/save-generated-tweet/<int:tweet_id>/', views.SaveGeneratedTweetAPIView.as_view()),
    path('api/approve-generated-tweet/<int:tweet_id>/', views.ApproveGeneratedTweetAPIView.as_view()),
    # ... other API endpoints
]
```

### 5.2 n8n Workflow Configuration

**HTTP Request Node Settings**:
- **Method**: POST
- **URL**: `http://127.0.0.1:8000/twitter/api/check-duplicate-tweet/`
- **Headers**: `Content-Type: application/json`
- **Body**: `{{ JSON.stringify($json) }}`
- **Authentication**: None (internal network)

**Environment Variables**:
```bash
# n8n workflow configuration
DJANGO_API_BASE_URL=http://127.0.0.1:8000
TWITTER_API_DUPLICATE_CHECK=/twitter/api/check-duplicate-tweet/
TWITTER_API_RECEIVE_TWEETS=/twitter/api/receive-tweets/
```

### 5.3 Testing the Integration

**Test Duplicate Check Endpoint**:
```bash
curl -X POST http://127.0.0.1:8000/twitter/api/check-duplicate-tweet/ \
  -H "Content-Type: application/json" \
  -d '{
    "execution_id": "test_exec_123",
    "source_url": "https://test.example.com",
    "tweets": [
      {
        "Tweet ID": "123456789",
        "URL": "https://x.com/user/status/123456789",
        "Content": "Test tweet content",
        "Likes": 5,
        "Retweets": 2,
        "Replies": 1,
        "Quotes": 0,
        "Views": 100,
        "Date": "Thu Aug 14 14:30:31 +0000 2025",
        "Status": "success",
        "Tweet": "https://twitter.com/user/status/123456789"
      }
    ]
  }'
```

**Test Receive Tweets Endpoint**:
```bash
curl -X POST http://127.0.0.1:8000/twitter/api/receive-tweets/ \
  -H "Content-Type: application/json" \
  -d '[{
    "campaign_batch": "test_batch_123",
    "tweets": [
      {
        "id": "test_tweet_1",
        "type": "scientific_compute",
        "content": "Test generated tweet content",
        "character_count": 30,
        "engagement_hook": "Test Hook",
        "ready_for_deployment": true,
        "status": "Brand Aligned"
      }
    ],
    "tweet_count": 1,
    "title": "Test Campaign"
  }]'
```

## Phase 6: Monitoring and Debugging

### 6.1 Database Monitoring

**Check Source Tweets**:
```sql
SELECT tweet_id, content, execution_id, processed_at 
FROM twitter_sourcetweet 
ORDER BY processed_at DESC 
LIMIT 10;
```

**Check Campaign Batches**:
```sql
SELECT batch_id, title, total_tweets, brand_alignment_score, created_at
FROM twitter_campaignbatch 
ORDER BY created_at DESC;
```

**Check Generated Tweets**:
```sql
SELECT gt.tweet_id, gt.type, gt.status, cb.batch_id
FROM twitter_generatedtweet gt
JOIN twitter_campaignbatch cb ON gt.campaign_batch_id = cb.id
ORDER BY gt.created_at DESC;
```

### 6.2 Logging and Debugging

**Django Logging**:
```python
import logging
logger = logging.getLogger(__name__)

# Key log messages to monitor
logger.info(f"Checking duplicates for execution {execution_id}, {len(tweets)} tweets")
logger.info(f"Successfully stored campaign batch {campaign_batch_id}: {tweets_stored} tweets")
logger.error(f"Error in check-duplicate-tweet: {str(e)}")
```

**n8n Debugging**:
- Monitor n8n execution logs for HTTP request failures
- Check response status codes (200 = success, 500 = server error)
- Verify JSON payload structure matches expected format

### 6.3 Performance Optimization

**Database Indexes**:
```python
# Ensure these indexes exist for optimal performance
class Meta:
    indexes = [
        models.Index(fields=['tweet_id']),  # SourceTweet
        models.Index(fields=['batch_id']),  # CampaignBatch
        models.Index(fields=['execution_id']),  # SourceTweet
        models.Index(fields=['processed_at']),  # SourceTweet
    ]
```

**Query Optimization**:
- Use `select_related()` for foreign key lookups
- Use `prefetch_related()` for many-to-many relationships
- Implement pagination for large datasets

## Phase 7: Production Deployment

### 7.1 Environment Configuration

**Django Settings**:
```python
# Production settings for n8n integration
ALLOWED_HOSTS = ['your-domain.com', 'n8n.coophive.network']
CSRF_TRUSTED_ORIGINS = ['https://n8n.coophive.network']

# Database configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'coophive_social',
        'USER': 'postgres_user',
        'PASSWORD': 'secure_password',
        'HOST': 'db.railway.app',
        'PORT': '5432',
    }
}
```

**n8n Production Configuration**:
```bash
# Update n8n workflow URLs for production
DJANGO_API_BASE_URL=https://your-django-app.railway.app
```

### 7.2 Security Considerations

**API Security**:
- Rate limiting for n8n endpoints
- IP whitelisting for n8n requests
- Request validation and sanitization
- Comprehensive error handling

**Data Security**:
- Encrypt sensitive tweet data
- Regular database backups
- Audit logging for all operations
- GDPR compliance for user data

### 7.3 Scaling Considerations

**Horizontal Scaling**:
- Load balancer for multiple Django instances
- Database connection pooling
- Redis for caching and session storage
- CDN for static assets

**Performance Monitoring**:
- APM tools (New Relic, DataDog)
- Database query monitoring
- API response time tracking
- Error rate monitoring

## Troubleshooting Guide

### Common Issues

**1. Connection Refused**
- **Cause**: Django server not running or wrong URL
- **Solution**: Verify server status and n8n configuration

**2. 404 Not Found**
- **Cause**: Incorrect URL path in n8n
- **Solution**: Check URL configuration in n8n workflow

**3. 500 Internal Server Error**
- **Cause**: Django application error
- **Solution**: Check Django logs for detailed error information

**4. Duplicate Key Errors**
- **Cause**: Attempting to store duplicate tweet_id or batch_id
- **Solution**: Verify duplicate detection logic is working

**5. JSON Parsing Errors**
- **Cause**: Invalid JSON structure from n8n
- **Solution**: Validate n8n output format matches expected schema

### Debug Commands

```bash
# Check Django server status
curl -I http://127.0.0.1:8000/twitter/api/check-duplicate-tweet/

# Test database connectivity
python manage.py shell -c "from twitter.models import SourceTweet; print(SourceTweet.objects.count())"

# Check recent logs
python manage.py runserver --verbosity=2

# Verify migrations
python manage.py showmigrations twitter
```

## Best Practices

### Development Workflow
1. **Test endpoints locally** before deploying to production
2. **Use version control** for n8n workflow changes
3. **Implement comprehensive logging** for debugging
4. **Monitor API performance** and response times
5. **Regular database backups** and testing

### Data Management
1. **Implement data retention policies** for old tweets
2. **Regular cleanup** of processed tweets
3. **Archive old campaign batches** after publishing
4. **Monitor database growth** and optimize queries

### Security
1. **Validate all input data** from n8n
2. **Sanitize tweet content** before storage
3. **Implement rate limiting** on API endpoints
4. **Regular security audits** of the integration

This comprehensive integration enables a complete social media intelligence pipeline from automated listening to AI-powered content generation and human-supervised publishing, all while maintaining data integrity and providing excellent user experience for content managers.
