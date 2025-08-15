# n8n Receive Generated Tweets API Documentation

## Overview

The `/twitter/api/receive-tweets/` endpoint receives AI-generated tweets from the n8n workflow and stores them in the Django database. This endpoint handles the output from the AI agents that create brand-aligned tweets based on the source tweets.

## Endpoint Details

- **URL**: `/twitter/api/receive-tweets/`
- **Method**: POST
- **Authentication**: None (designed for n8n workflow integration)
- **Content-Type**: `application/json`

## n8n Workflow Integration

This endpoint integrates with the X-Bot n8n workflow (`X_Bot (24).json`) after the AI generation phase:

1. **Source tweets processed** → AI agents generate brand-aligned content
2. **Generated tweets sent** → Django API for storage
3. **Campaign batch created** → Ready for review and approval
4. **Response returned** → Confirms successful storage

### n8n Configuration

In the n8n workflow, configure the HTTP Request node:

```json
{
  "method": "POST",
  "url": "http://127.0.0.1:8000/twitter/api/receive-tweets/",
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

## Input Format

The endpoint accepts the exact format produced by the n8n AI workflow:

```json
[
  {
    "campaign_batch": "batch_2025-08-14_16-10",
    "generated_at": "2025-08-14T16:10:46.172Z",
    "analysis_summary": {
      "input_batch_size": 3,
      "dominant_themes": [
        "brand_alignment",
        "cyber_architect",
        "agent_first"
      ],
      "top_engagement_score": 1,
      "content_strategy": "Multi-agent brand alignment with Cyber Architect voice",
      "brand_alignment_score": 9
    },
    "tweets": [
      {
        "id": "batch_2025-08-14_16-10-tweet-1",
        "type": "scientific_compute",
        "content": "Architecting research workflows: CoopHive designs the rails for immediate compute access. Blueprint your discoveries, execute without delay. Agents orchestrate resources on demand. #DecentralizedCompute",
        "character_count": 218,
        "engagement_hook": "Compute Without Queues",
        "coophive_elements": [
          "agent-first",
          "compute-orchestration",
          "queue-elimination"
        ],
        "discord_voice_patterns": [
          "blueprint-precision",
          "architectural-clarity",
          "agent-centric",
          "autonomous-orchestration"
        ],
        "theme_connection": "Refined tweets to fully embody the Cyber Architect persona, foregrounding agent-first architecture, game-theoretic primitives, and marketplace composability.",
        "timestamp": "2025-08-14T16:10:46.172Z",
        "ready_for_deployment": true,
        "campaign_batch": "batch_2025-08-14_16-10",
        "status": "Brand Aligned",
        "is_edited": false
      }
    ],
    "tweet_count": 3,
    "ready_for_deployment": 3,
    "title": "Multi-Agent Brand-Aligned Content",
    "description": "AI-generated tweets optimized for CoopHive brand voice and audience targeting",
    "source_type": "multi_agent_automation"
  }
]
```

### Input Field Descriptions

#### Campaign Level Fields
- **campaign_batch**: Unique identifier for the campaign batch (e.g., "batch_2025-08-14_16-10")
- **generated_at**: ISO timestamp when the content was generated
- **analysis_summary**: AI analysis metadata including themes and scores
- **tweet_count**: Total number of tweets in the batch
- **ready_for_deployment**: Number of tweets ready for publishing
- **title**: Human-readable title for the campaign
- **description**: Description of the campaign content
- **source_type**: Source of generation (e.g., "multi_agent_automation")

#### Tweet Level Fields
- **id**: Unique tweet identifier within the batch
- **type**: Tweet category (scientific_compute, infrastructure_optimization, developer_tools, autonomous_systems)
- **content**: The actual tweet content (≤280 characters)
- **character_count**: Number of characters in the tweet
- **engagement_hook**: CTA or engagement strategy
- **coophive_elements**: Array of CoopHive brand elements referenced
- **discord_voice_patterns**: Array of voice pattern tags used
- **theme_connection**: Explanation of thematic alignment
- **timestamp**: When the tweet was generated
- **ready_for_deployment**: Boolean indicating if tweet is ready to publish
- **status**: Current status (e.g., "Brand Aligned")
- **is_edited**: Boolean indicating if tweet has been manually edited

## Output Format

The endpoint returns a simple confirmation in the exact format expected by n8n:

```json
[
  {
    "campaign_batch": "batch_2025-08-14_16-10",
    "message": "Received 3 tweets (saved to database)",
    "status": "success"
  }
]
```

### Output Field Descriptions

- **campaign_batch**: Echo of the input campaign batch ID
- **message**: Human-readable success message with count of stored tweets
- **status**: "success" or "error"

## Database Storage

The endpoint stores data in two main models:

### CampaignBatch Model

Stores campaign-level metadata:

```python
class CampaignBatch(models.Model):
    batch_id = models.CharField(max_length=100, unique=True)
    analysis_summary = models.JSONField()
    total_tweets = models.IntegerField()
    ready_for_deployment = models.IntegerField()
    source_type = models.CharField(max_length=50)
    title = models.CharField(max_length=255)
    description = models.TextField()
    brand_alignment_score = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default="Draft")
```

### GeneratedTweet Model

Stores individual tweet data:

```python
class GeneratedTweet(models.Model):
    campaign_batch = models.ForeignKey(CampaignBatch, on_delete=models.CASCADE)
    tweet_id = models.CharField(max_length=100)
    type = models.CharField(max_length=50)
    content = models.TextField()
    character_count = models.IntegerField()
    engagement_hook = models.TextField()
    coophive_elements = models.JSONField()
    discord_voice_patterns = models.JSONField()
    theme_connection = models.TextField()
    ready_for_deployment = models.BooleanField()
    status = models.CharField(max_length=20)
    is_edited = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
```

## Duplicate Handling

The endpoint includes smart duplicate handling:

1. **Campaign Batch**: Uses `get_or_create()` to avoid duplicate batches
2. **Individual Tweets**: Checks for existing `tweet_id` within the same campaign batch
3. **Response Accuracy**: Only counts actually stored tweets in the response message

## Error Handling

The endpoint includes comprehensive error handling:

```json
{
  "campaign_batch": "batch_id_if_available",
  "message": "Error storing tweets: [error details]",
  "status": "error"
}
```

Common error scenarios:
- Invalid JSON payload
- Missing required fields (campaign_batch, tweets)
- Database connection issues
- Invalid tweet data structure

## Testing

### Test with curl

```bash
curl -X POST http://127.0.0.1:8000/twitter/api/receive-tweets/ \
  -H "Content-Type: application/json" \
  -d '[{
    "campaign_batch": "test_batch_123",
    "generated_at": "2025-08-14T16:10:46.172Z",
    "analysis_summary": {
      "brand_alignment_score": 8.5
    },
    "tweets": [
      {
        "id": "test_tweet_1",
        "type": "scientific_compute",
        "content": "Test tweet content for CoopHive #DecentralizedCompute",
        "character_count": 55,
        "engagement_hook": "Test Hook",
        "coophive_elements": ["agent-first"],
        "discord_voice_patterns": ["blueprint-precision"],
        "theme_connection": "Test connection",
        "ready_for_deployment": true,
        "status": "Brand Aligned",
        "is_edited": false
      }
    ],
    "tweet_count": 1,
    "ready_for_deployment": 1,
    "title": "Test Campaign",
    "description": "Test campaign description",
    "source_type": "multi_agent_automation"
  }]'
```

### Test with Python

```python
import requests
import json

url = "http://127.0.0.1:8000/twitter/api/receive-tweets/"
data = [{
    "campaign_batch": "test_batch_123",
    "generated_at": "2025-08-14T16:10:46.172Z",
    "tweets": [
        {
            "id": "test_tweet_1",
            "type": "scientific_compute",
            "content": "Test tweet content",
            "character_count": 18,
            "engagement_hook": "Test Hook",
            "coophive_elements": ["agent-first"],
            "discord_voice_patterns": ["blueprint-precision"],
            "ready_for_deployment": True,
            "status": "Brand Aligned",
            "is_edited": False
        }
    ],
    "tweet_count": 1,
    "title": "Test Campaign",
    "source_type": "multi_agent_automation"
}]

response = requests.post(url, json=data)
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")
```

## Monitoring and Debugging

### Logs

The endpoint logs important events:

```python
logger.info(f"Receiving generated tweets for batch {campaign_batch_id}")
logger.info(f"Successfully stored campaign batch {campaign_batch_id}: {tweets_stored} tweets")
logger.error(f"Error in receive-tweets: {str(e)}")
```

### Database Queries

Monitor campaign batches and generated tweets:

```sql
-- Check recent campaign batches
SELECT batch_id, title, total_tweets, brand_alignment_score, created_at
FROM twitter_campaignbatch 
ORDER BY created_at DESC 
LIMIT 10;

-- Check generated tweets for a batch
SELECT tweet_id, type, character_count, ready_for_deployment, status
FROM twitter_generatedtweet 
WHERE campaign_batch_id = (
    SELECT id FROM twitter_campaignbatch WHERE batch_id = 'batch_2025-08-14_16-10'
);

-- Count tweets by campaign batch
SELECT cb.batch_id, cb.title, COUNT(gt.id) as tweet_count
FROM twitter_campaignbatch cb
LEFT JOIN twitter_generatedtweet gt ON cb.id = gt.campaign_batch_id
GROUP BY cb.id, cb.batch_id, cb.title
ORDER BY cb.created_at DESC;
```

## Integration with Review Interface

The stored data integrates with the campaign review interface:

1. **Campaign List**: `/twitter/generate-tweets/` shows all campaign batches
2. **Review Interface**: `/twitter/review/{batch_id}/` allows editing and approval
3. **Tweet Management**: Individual tweets can be edited, approved, or rejected
4. **Publishing Pipeline**: Approved tweets can be posted to X.com

## Production Considerations

1. **Rate Limiting**: Consider adding rate limiting for production use
2. **Authentication**: Add authentication if exposing publicly
3. **Monitoring**: Set up monitoring for failed requests
4. **Database Indexing**: Ensure proper indexing on `batch_id` and `tweet_id`
5. **Backup**: Regular backup of campaign and tweet data
6. **Validation**: Add additional validation for tweet content and metadata

## Integration Checklist

- [ ] n8n workflow configured with correct endpoint URL
- [ ] Content-Type header set to `application/json`
- [ ] Django server running and accessible from n8n
- [ ] Database migrations applied (`python manage.py migrate`)
- [ ] CampaignBatch and GeneratedTweet models created
- [ ] Review interface accessible for campaign management
- [ ] Test with sample data to verify functionality

## Troubleshooting

### Common Issues

1. **Connection Refused**: Ensure Django server is running
2. **404 Not Found**: Check URL path and Django URL configuration
3. **500 Internal Server Error**: Check Django logs for detailed error
4. **Foreign Key Errors**: Ensure CampaignBatch is created before tweets
5. **JSON Parsing Errors**: Verify input data structure

### Debug Commands

```bash
# Check if endpoint is accessible
curl -I http://127.0.0.1:8000/twitter/api/receive-tweets/

# Check Django logs
python manage.py runserver --verbosity=2

# Test database models
python manage.py shell -c "
from twitter.models import CampaignBatch, GeneratedTweet
print(f'Campaign Batches: {CampaignBatch.objects.count()}')
print(f'Generated Tweets: {GeneratedTweet.objects.count()}')
"
```

## Workflow Integration

This endpoint works in conjunction with:

1. **`/twitter/api/check-duplicate-tweet/`** - Processes source tweets first
2. **n8n AI Agents** - Generate brand-aligned content
3. **`/twitter/api/receive-tweets/`** - Stores generated content (this endpoint)
4. **Review Interface** - Manual review and approval
5. **Publishing APIs** - Final posting to social media

This creates a complete pipeline from social listening to content publication, with human oversight and approval at key stages.

The API endpoint provides seamless integration between the n8n AI workflow and Django application, enabling efficient storage and management of AI-generated social media content for the CoopHive brand.
