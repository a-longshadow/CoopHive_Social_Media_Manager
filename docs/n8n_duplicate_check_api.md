# n8n Duplicate Check API Documentation

## Overview

The `/twitter/api/check-duplicate-tweet/` endpoint is the primary integration point between the n8n workflow and the Django Twitter app. This endpoint receives tweets from the n8n social listening workflow, checks for duplicates, stores new tweets, and returns filtered data back to n8n.

## Endpoint Details

- **URL**: `/twitter/api/check-duplicate-tweet/`
- **Method**: POST
- **Authentication**: None (designed for n8n workflow integration)
- **Content-Type**: `application/json`

## n8n Workflow Integration

This endpoint integrates with the X-Bot n8n workflow (`X_Bot (24).json`) at the "HTTP Request" node which:

1. **Collects tweets** from social media accounts
2. **Sends to Django** for duplicate checking
3. **Receives filtered data** back from Django
4. **Continues processing** with only new tweets

### n8n Configuration

In the n8n workflow, configure the HTTP Request node:

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

## Input Format

The endpoint accepts the exact format produced by the n8n workflow:

```json
{
  "execution_id": "exec_2025-08-14_1607_n8n_r26hp94b",
  "source_url": "https://n8n.coophive.network",
  "tweets": [
    {
      "Tweet ID": "1956000485229441027",
      "URL": "https://x.com/hugo_larochelle/status/1956000485229441027",
      "Content": "@jpineau1 @cohere Congratulations Joëlle!!",
      "Likes": 0,
      "Retweets": 0,
      "Replies": 0,
      "Quotes": 0,
      "Views": 593,
      "Date": "Thu Aug 14 14:30:31 +0000 2025",
      "Status": "success",
      "Tweet": "https://twitter.com/hugo_larochelle/status/1956000485229441027"
    }
  ],
  "batch_metadata": {
    "total_tweets": 3,
    "processing_timestamp": "2025-08-14T16:07:32.837Z",
    "accounts_processed": 6,
    "n8n_workflow_id": "M7nME7h8w2Hyi4T6",
    "n8n_execution_id": "2582",
    "original_total": 119,
    "filtering_applied": true,
    "filtering_timestamp": "2025-08-14T16:07:32.893Z"
  }
}
```

### Input Field Descriptions

- **execution_id**: Unique identifier for this n8n execution
- **source_url**: Source of the data (typically n8n instance URL)
- **tweets**: Array of tweet objects with Twitter API data
- **batch_metadata**: Optional metadata about the batch processing

## Output Format

The endpoint returns data in the exact format expected by n8n:

```json
{
  "data": {
    "duplicate_ids": [],
    "execution_id": "exec_2025-08-14_1607_n8n_r26hp94b",
    "new_tweets": [
      {
        "Content": "@jpineau1 @cohere Congratulations Joëlle!!",
        "Date": "Thu Aug 14 14:30:31 +0000 2025",
        "Likes": 0,
        "Quotes": 0,
        "Replies": 0,
        "Retweets": 0,
        "Status": "success",
        "Tweet": "https://twitter.com/hugo_larochelle/status/1956000485229441027",
        "Tweet ID": "1956000485229441027",
        "URL": "https://x.com/hugo_larochelle/status/1956000485229441027",
        "Views": 593
      }
    ],
    "source_url": "https://n8n.coophive.network"
  },
  "debug_info": {
    "error_count": 0,
    "processed_count": 3,
    "saved_count": 3
  },
  "message": "✅ Success: All 3 tweets are new and have been saved to database",
  "status": "success",
  "summary": {
    "duplicates_found": 0,
    "execution_id_duplicates": 0,
    "new_tweets_found": 3,
    "saved_to_database": 3,
    "total_processed": 3,
    "tweet_id_duplicates": 0
  }
}
```

### Output Field Descriptions

- **data.new_tweets**: Array of non-duplicate tweets (same format as input)
- **data.duplicate_ids**: Array of duplicate tweet IDs found
- **data.execution_id**: Echo of the input execution ID
- **data.source_url**: Echo of the input source URL
- **debug_info**: Technical information for debugging
- **message**: Human-readable success/error message
- **status**: "success" or "error"
- **summary**: Detailed statistics about the processing

## Duplicate Detection Logic

The endpoint uses the following logic to detect duplicates:

1. **Tweet ID Check**: Primary duplicate detection based on `tweet_id` field
2. **Database Storage**: New tweets are stored in the `SourceTweet` model
3. **Atomic Operations**: All database operations are wrapped in transactions
4. **Logging**: All duplicate checks are logged for debugging

### SourceTweet Model

New tweets are stored with these fields:

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
    status = models.CharField(max_length=50, default="success")
    tweet_url = models.URLField()
    execution_id = models.CharField(max_length=255)
    source_url = models.CharField(max_length=255)
    processed_at = models.DateTimeField(auto_now_add=True)
    is_processed = models.BooleanField(default=False)
```

## Date Format Handling

The endpoint handles multiple date formats:

1. **ISO Format**: `2025-08-14T16:07:32.837Z`
2. **Twitter Format**: `Thu Aug 14 14:30:31 +0000 2025`

Date parsing uses both `datetime.fromisoformat()` and `dateutil.parser.parse()` for maximum compatibility.

## Error Handling

The endpoint includes comprehensive error handling:

```json
{
  "status": "error",
  "message": "Error processing tweets: [error details]",
  "data": null
}
```

Common error scenarios:
- Invalid JSON payload
- Missing required fields
- Database connection issues
- Date parsing errors

## Testing

### Test with curl

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

### Test with Python

```python
import requests
import json

url = "http://127.0.0.1:8000/twitter/api/check-duplicate-tweet/"
data = {
    "execution_id": "test_exec_123",
    "source_url": "https://test.example.com",
    "tweets": [
        {
            "Tweet ID": "123456789",
            "Content": "Test tweet content",
            "Likes": 5,
            "Date": "Thu Aug 14 14:30:31 +0000 2025"
        }
    ]
}

response = requests.post(url, json=data)
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")
```

## Monitoring and Debugging

### Logs

The endpoint logs important events:

```python
logger.info(f"Checking duplicates for execution {execution_id}, {len(tweets)} tweets")
logger.debug(f"Duplicate found: {tweet_id}")
logger.debug(f"Stored new tweet: {tweet_id}")
logger.info(f"Duplicate check complete: {len(new_tweets)} new, {duplicates_found} duplicates")
```

### Database Queries

Monitor the `SourceTweet` table:

```sql
-- Check recent tweets
SELECT tweet_id, content, execution_id, processed_at 
FROM twitter_sourcetweet 
ORDER BY processed_at DESC 
LIMIT 10;

-- Count tweets by execution
SELECT execution_id, COUNT(*) as tweet_count
FROM twitter_sourcetweet 
GROUP BY execution_id 
ORDER BY MAX(processed_at) DESC;
```

## Production Considerations

1. **Rate Limiting**: Consider adding rate limiting for production use
2. **Authentication**: Add authentication if exposing publicly
3. **Monitoring**: Set up monitoring for failed requests
4. **Database Indexing**: Ensure `tweet_id` is properly indexed
5. **Backup**: Regular backup of `SourceTweet` data

## Integration Checklist

- [ ] n8n workflow configured with correct endpoint URL
- [ ] Content-Type header set to `application/json`
- [ ] Django server running and accessible from n8n
- [ ] Database migrations applied (`python manage.py migrate`)
- [ ] Logging configured for debugging
- [ ] Test with sample data to verify functionality

## Troubleshooting

### Common Issues

1. **Connection Refused**: Ensure Django server is running
2. **404 Not Found**: Check URL path and Django URL configuration
3. **500 Internal Server Error**: Check Django logs for detailed error
4. **Date Parsing Errors**: Verify date format in input data
5. **Database Errors**: Ensure migrations are applied

### Debug Commands

```bash
# Check if endpoint is accessible
curl -I http://127.0.0.1:8000/twitter/api/check-duplicate-tweet/

# Check Django logs
python manage.py runserver --verbosity=2

# Test database connection
python manage.py shell -c "from twitter.models import SourceTweet; print(SourceTweet.objects.count())"
```

This API endpoint provides seamless integration between the n8n workflow and Django application, ensuring efficient duplicate detection and data flow for the CoopHive social media intelligence system.
