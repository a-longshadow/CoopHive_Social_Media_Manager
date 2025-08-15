# API Documentation

## Overview

The CoopHive Social Media Manager provides comprehensive REST APIs for social media platform management, n8n workflow integration, and content management. All APIs follow consistent patterns and authentication methods.

## Authentication

### Bearer Token Authentication
```http
Authorization: Bearer <your-access-token>
```

### CSRF Protection
For non-GET requests, include the CSRF token:
```http
X-CSRFToken: <csrf-token>
```

### n8n Integration Endpoints
n8n workflow endpoints do not require authentication for seamless automation.

## Common Response Format
```json
{
    "status": "success|error",
    "data": {}, 
    "message": "Human readable message",
    "errors": []  // Present only when status is "error"
}
```

## n8n Workflow Integration APIs

### Check Duplicate Tweets
**Primary endpoint for n8n social listening workflow**

```http
POST /twitter/api/check-duplicate-tweet/
Content-Type: application/json

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
  ]
}
```

**Response:**
```json
{
  "data": {
    "duplicate_ids": [],
    "execution_id": "exec_2025-08-14_1607_n8n_r26hp94b",
    "new_tweets": [...],
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

### Receive Generated Tweets
**Endpoint for storing AI-generated tweets from n8n workflow**

```http
POST /twitter/api/receive-tweets/
Content-Type: application/json

[{
  "campaign_batch": "batch_2025-08-14_16-10",
  "generated_at": "2025-08-14T16:10:46.172Z",
  "analysis_summary": {
    "brand_alignment_score": 9,
    "dominant_themes": ["brand_alignment", "cyber_architect", "agent_first"]
  },
  "tweets": [
    {
      "id": "batch_2025-08-14_16-10-tweet-1",
      "type": "scientific_compute",
      "content": "AI-generated tweet content...",
      "character_count": 218,
      "engagement_hook": "Compute Without Queues",
      "coophive_elements": ["agent-first", "compute-orchestration"],
      "ready_for_deployment": true,
      "status": "Brand Aligned"
    }
  ],
  "tweet_count": 3,
  "title": "Multi-Agent Brand-Aligned Content",
  "source_type": "multi_agent_automation"
}]
```

**Response:**
```json
[{
  "campaign_batch": "batch_2025-08-14_16-10",
  "message": "Received 3 tweets (saved to database)",
  "status": "success"
}]
```

## Twitter/X.com Platform APIs

### Scraped Tweets Management

#### Get Tweet Details
```http
GET /twitter/api/tweet-details/{tweet_id}/
```

#### Delete Single Tweet
```http
DELETE /twitter/api/delete-tweet/{tweet_id}/
```

#### Bulk Delete Tweets
```http
POST /twitter/api/bulk-delete-tweets/
Content-Type: application/json

{
  "tweet_ids": [1, 2, 3, 4, 5]
}
```

#### Export Tweets
```http
GET /twitter/sourcetweet/export/?format=csv
```

### Generated Tweet Management

#### Save Generated Tweet
```http
POST /twitter/api/save-generated-tweet/{tweet_id}/
Content-Type: application/json

{
  "content": "Updated tweet content..."
}
```

#### Approve Generated Tweet
```http
POST /twitter/api/approve-generated-tweet/{tweet_id}/
```

#### Reject Generated Tweet
```http
POST /twitter/api/reject-generated-tweet/{tweet_id}/
```

#### Post Tweet to X.com
```http
POST /twitter/api/post-tweet-to-x/{tweet_id}/
```

### Campaign Management

#### Generate Tweets Dashboard
```http
GET /twitter/generate-tweets/
```

#### Campaign Review Interface
```http
GET /twitter/review/{campaign_batch}/
```

### Traditional Post Management

#### Create Post
```http
POST /twitter/api/post/
Content-Type: application/json

{
    "content": "Tweet content #hashtag",
    "media": ["media_id1"],
    "schedule_time": "2025-08-14T15:00:00Z"  // Optional
}
```

#### Schedule Tweet
```http
POST /twitter/api/schedule/
Content-Type: application/json

{
    "post_id": "123",
    "schedule_time": "2025-08-14T15:00:00Z"
}
```

#### Get Analytics
```http
GET /twitter/analytics/?start_date=2025-07-14&end_date=2025-08-14
```

## LinkedIn API

### Post Management

#### Create Standard Post
```http
POST /linkedin/api/publish/
Content-Type: application/json

{
    "content": "LinkedIn post content #innovation",
    "visibility": "public",  // public, connections, logged-in
    "media": ["media_id1", "media_id2"],
    "schedule_time": "2025-08-14T15:00:00Z"  // Optional
}
```

#### Create Article Post
```http
POST /linkedin/articles/new/
Content-Type: application/json

{
    "content": "Article introduction...",
    "article_url": "https://example.com/article",
    "title": "Article Title"
}
```

#### Create Document Post
```http
POST /linkedin/documents/new/
Content-Type: application/json

{
    "content": "Document description...",
    "document_title": "Document Title",
    "media": ["document_file_id"]
}
```

#### Schedule Post
```http
POST /linkedin/api/schedule/
Content-Type: application/json

{
    "post_id": "123",
    "schedule_time": "2025-08-14T15:00:00Z"
}
```

#### Get Analytics
```http
GET /linkedin/analytics/?start_date=2025-07-14&end_date=2025-08-14
```

**Response:**
```json
{
    "status": "success",
    "data": {
        "impressions": 1250,
        "engagement_rate": 4.2,
        "click_through_rate": 2.1,
        "posts": [...]
    }
}
```

### Media Management
```http
POST /linkedin/media/upload/
Content-Type: multipart/form-data

{
    "file": <file-data>,
    "type": "image|video|document",
    "alt_text": "Optional alt text"
}
```

## Farcaster API

### Cast Management

#### Create Cast
```http
POST /farcaster/api/publish/
Content-Type: application/json

{
    "content": "Farcaster cast content",
    "channel": "coophive",  // Optional channel
    "parent_cast_hash": "0x123...",  // Optional for replies
    "media": ["media_id1"],
    "schedule_time": "2025-08-14T15:00:00Z"  // Optional
}
```

#### Schedule Cast
```http
POST /farcaster/api/schedule/
Content-Type: application/json

{
    "cast_id": "123",
    "schedule_time": "2025-08-14T15:00:00Z"
}
```

#### Get Analytics
```http
GET /farcaster/analytics/?start_date=2025-07-14&end_date=2025-08-14
```

**Response:**
```json
{
    "status": "success",
    "data": {
        "recasts": 45,
        "watches": 890,
        "reactions": {
            "like": 23,
            "love": 12,
            "wow": 5
        },
        "casts": [...]
    }
}
```

### Media Management
```http
POST /farcaster/media/upload/
Content-Type: multipart/form-data

{
    "file": <file-data>,
    "type": "image|video",
    "alt_text": "Optional alt text"
}
```

## Bluesky API

### Post Management

#### Create Post
```http
POST /bluesky/api/publish/
Content-Type: application/json

{
    "content": "Bluesky post content",
    "reply_root": "at://did:plc:123.../...",  // Optional for replies
    "reply_parent": "at://did:plc:123.../...",  // Optional for replies
    "self_labels": ["tag1", "tag2"],  // Optional content labels
    "media": ["media_id1"],
    "schedule_time": "2025-08-14T15:00:00Z"  // Optional
}
```

#### Schedule Post
```http
POST /bluesky/api/schedule/
Content-Type: application/json

{
    "post_id": "123",
    "schedule_time": "2025-08-14T15:00:00Z"
}
```

#### Get Analytics
```http
GET /bluesky/analytics/?start_date=2025-07-14&end_date=2025-08-14
```

**Response:**
```json
{
    "status": "success",
    "data": {
        "reposts": 34,
        "likes": 156,
        "replies": 12,
        "posts": [...]
    }
}
```

## Media Management

### Upload Media
```http
POST /platform/media/upload/
Content-Type: multipart/form-data

{
    "file": <file-data>,
    "type": "image|video|document",
    "alt_text": "Optional alt text"
}
```

### Delete Media
```http
DELETE /platform/media/<media_id>/delete/
```

## Error Codes

| Code | Description             |
|------|------------------------|
| 400  | Bad Request            |
| 401  | Unauthorized           |
| 403  | Forbidden             |
| 404  | Not Found             |
| 429  | Rate Limit Exceeded   |
| 500  | Server Error          |

## Rate Limiting

- 100 requests per minute per user
- 1000 requests per hour per user
- Exceeded limits return 429 status code

## Webhook Support

### Register Webhook
```http
POST /api/webhooks/register/
Content-Type: application/json

{
    "url": "https://your-domain.com/webhook",
    "events": ["post.created", "post.published"],
    "platforms": ["linkedin", "twitter"]
}
```

### Webhook Events
- post.created
- post.scheduled
- post.published
- post.failed
- analytics.updated
