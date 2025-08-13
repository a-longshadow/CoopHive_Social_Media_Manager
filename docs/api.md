# API Documentation

## Overview

The CoopHive Social Media Manager provides REST APIs for each social media platform integration. All APIs follow consistent patterns and authentication methods.

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

## Common Response Format
```json
{
    "status": "success|error",
    "data": {}, 
    "message": "Human readable message",
    "errors": []  // Present only when status is "error"
}
```

## Platform APIs

### LinkedIn API

#### Create Post
```http
POST /linkedin/api/post/
Content-Type: application/json

{
    "content": "Post content",
    "media": ["media_id1", "media_id2"],
    "schedule_time": "2025-08-14T15:00:00Z"  // Optional
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

### Twitter (X.com) API

Similar endpoints and structures as LinkedIn:
- POST /twitter/api/post/
- POST /twitter/api/schedule/
- GET /twitter/analytics/

### Farcaster API

Endpoints follow the same pattern:
- POST /farcaster/api/post/
- POST /farcaster/api/schedule/
- GET /farcaster/analytics/

### Bluesky API

Same consistent pattern:
- POST /bluesky/api/post/
- POST /bluesky/api/schedule/
- GET /bluesky/analytics/

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
