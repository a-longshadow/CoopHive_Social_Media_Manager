from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, View
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.db import transaction, models
import json
import logging
from dateutil import parser as date_parser
from .models import SourceTweet, CampaignBatch, GeneratedTweet

logger = logging.getLogger(__name__)

# ============================================================================
# FLASK API COMPATIBILITY ENDPOINTS - CRITICAL FOR N8N INTEGRATION
# ============================================================================

@method_decorator(csrf_exempt, name='dispatch')
class CheckDuplicateTweetAPIView(APIView):
    """
    CRITICAL: Primary endpoint that n8n hits first
    Check for duplicate tweets, store non-duplicates, return filtered data to n8n
    """
    authentication_classes = []  # No auth required for n8n
    permission_classes = []

    def post(self, request):
        try:
            data = request.data
            
            # Handle array format from n8n (like SAMPLE_SIMPLE_IN.JSON)
            if isinstance(data, list) and len(data) > 0:
                data = data[0]  # Extract first object from array
            
            # Handle nested data format (like SAMPLE_DETAILED_IN.JSON)
            if 'data' in data and 'tweets' in data['data']:
                # Detailed format: data.data.tweets
                tweets = data['data']['tweets']
                execution_id = data.get('execution_id', f"exec_{data.get('msg', 'unknown')}")
                source_url = data.get('source_url', 'api_detailed')
                batch_metadata = data.get('batch_metadata', {})
            else:
                # Simple format: data.tweets
                execution_id = data.get('execution_id')
                source_url = data.get('source_url', 'unknown')
                tweets = data.get('tweets', [])
                batch_metadata = data.get('batch_metadata', {})
            
            logger.info(f"Checking duplicates for execution {execution_id}, {len(tweets)} tweets")
            
            new_tweets = []
            duplicates_found = 0
            
            with transaction.atomic():
                for tweet_data in tweets:
                    # Handle different field formats
                    if 'Tweet ID' in tweet_data:
                        # Simple format (SAMPLE_SIMPLE_IN.JSON)
                        tweet_id = tweet_data.get('Tweet ID')
                        content = tweet_data.get('Content', '')
                        likes = tweet_data.get('Likes', 0)
                        retweets = tweet_data.get('Retweets', 0)
                        replies = tweet_data.get('Replies', 0)
                        quotes = tweet_data.get('Quotes', 0)
                        views = tweet_data.get('Views', 0)
                        url = tweet_data.get('URL', '')
                        tweet_url = tweet_data.get('Tweet', '')
                        date_str = tweet_data.get('Date', '')
                        status_val = tweet_data.get('Status', 'success')
                    else:
                        # Detailed format (SAMPLE_DETAILED_IN.JSON)
                        tweet_id = tweet_data.get('id')
                        content = tweet_data.get('text', '')
                        likes = tweet_data.get('likeCount', 0)
                        retweets = tweet_data.get('retweetCount', 0)
                        replies = tweet_data.get('replyCount', 0)
                        quotes = tweet_data.get('quoteCount', 0)
                        views = tweet_data.get('viewCount', 0)
                        url = tweet_data.get('url', '')
                        tweet_url = tweet_data.get('twitterUrl', '')
                        date_str = tweet_data.get('createdAt', '')
                        status_val = 'success'
                    
                    if not tweet_id:
                        continue
                    
                    # Check if tweet already exists
                    if SourceTweet.objects.filter(tweet_id=str(tweet_id)).exists():
                        duplicates_found += 1
                        logger.debug(f"Duplicate found: {tweet_id}")
                        continue
                    
                    # Parse date - handle multiple formats from n8n
                    try:
                        if date_str:
                            # Try ISO format first (2025-08-14T16:07:32.837Z)
                            if 'T' in date_str:
                                tweet_date = timezone.datetime.fromisoformat(
                                    date_str.replace('Z', '+00:00')
                                )
                            else:
                                # Handle Twitter format: "Thu Aug 14 14:30:31 +0000 2025"
                                tweet_date = date_parser.parse(date_str)
                                if tweet_date.tzinfo is None:
                                    tweet_date = timezone.make_aware(tweet_date)
                        else:
                            tweet_date = timezone.now()
                    except (ValueError, AttributeError, ImportError):
                        tweet_date = timezone.now()
                    
                    # Create new SourceTweet
                    source_tweet = SourceTweet.objects.create(
                        tweet_id=str(tweet_id),
                        url=url,
                        content=content,
                        likes=int(likes),
                        retweets=int(retweets),
                        replies=int(replies),
                        quotes=int(quotes),
                        views=int(views),
                        date=tweet_date,
                        status=status_val,
                        tweet_url=tweet_url,
                        execution_id=execution_id,
                        source_url=source_url
                    )
                    
                    # Add to new tweets list (preserve original format)
                    new_tweets.append(tweet_data)
                    logger.debug(f"Stored new tweet: {tweet_id}")
            
            # Prepare response in exact n8n expected format (matching out.json)
            response_data = {
                "data": {
                    "duplicate_ids": [],  # Could be populated with actual duplicate IDs if needed
                    "execution_id": execution_id,
                    "new_tweets": new_tweets,
                    "source_url": source_url
                },
                "debug_info": {
                    "error_count": 0,
                    "processed_count": len(tweets),
                    "saved_count": len(new_tweets)
                },
                "message": f"✅ Success: All {len(new_tweets)} tweets are new and have been saved to database" if duplicates_found == 0 else f"✅ Success: {len(new_tweets)} new tweets saved, {duplicates_found} duplicates found",
                "status": "success",
                "summary": {
                    "duplicates_found": duplicates_found,
                    "execution_id_duplicates": 0,  # Could track execution ID duplicates separately
                    "new_tweets_found": len(new_tweets),
                    "saved_to_database": len(new_tweets),
                    "total_processed": len(tweets),
                    "tweet_id_duplicates": duplicates_found
                }
            }
            
            logger.info(f"Duplicate check complete: {len(new_tweets)} new, {duplicates_found} duplicates")
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error in check-duplicate-tweet: {str(e)}")
            return Response({
                "status": "error",
                "message": f"Error processing tweets: {str(e)}",
                "data": None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@method_decorator(csrf_exempt, name='dispatch')
class ReceiveTweetsAPIView(APIView):
    """
    Store generated tweet batches from n8n AI workflow
    """
    authentication_classes = []  # No auth required for n8n
    permission_classes = []

    def post(self, request):
        try:
            data = request.data
            
            # Handle array format from n8n (like in.json)
            if isinstance(data, list) and len(data) > 0:
                data = data[0]  # Extract first object from array
            
            campaign_batch_id = data.get('campaign_batch')
            
            logger.info(f"Receiving generated tweets for batch {campaign_batch_id}")
            
            with transaction.atomic():
                # Create or get campaign batch
                campaign_batch, created = CampaignBatch.objects.get_or_create(
                    batch_id=campaign_batch_id,
                    defaults={
                        'analysis_summary': data.get('analysis_summary', {}),
                        'total_tweets': data.get('tweet_count', 0),
                        'ready_for_deployment': data.get('ready_for_deployment', 0),
                        'source_type': data.get('source_type', 'multi_agent_automation'),
                        'title': data.get('title', 'Generated Content'),
                        'description': data.get('description', ''),
                        'brand_alignment_score': data.get('analysis_summary', {}).get('brand_alignment_score')
                    }
                )
                
                # Store individual tweets
                tweets_stored = 0
                for tweet_data in data.get('tweets', []):
                    # Check if tweet already exists to avoid duplicates
                    if not GeneratedTweet.objects.filter(
                        campaign_batch=campaign_batch,
                        tweet_id=tweet_data.get('id')
                    ).exists():
                        GeneratedTweet.objects.create(
                            campaign_batch=campaign_batch,
                            tweet_id=tweet_data.get('id'),
                            type=tweet_data.get('type', 'generated'),
                            content=tweet_data.get('content'),
                            character_count=tweet_data.get('character_count', len(tweet_data.get('content', ''))),
                            engagement_hook=tweet_data.get('engagement_hook', ''),
                            coophive_elements=tweet_data.get('coophive_elements', []),
                            discord_voice_patterns=tweet_data.get('discord_voice_patterns', []),
                            theme_connection=tweet_data.get('theme_connection', ''),
                            ready_for_deployment=tweet_data.get('ready_for_deployment', True),
                            status=tweet_data.get('status', 'Brand Aligned'),
                            is_edited=tweet_data.get('is_edited', False)
                        )
                        tweets_stored += 1
            
            # Return response in exact format expected by n8n (matching out.json)
            response_data = {
                "campaign_batch": campaign_batch_id,
                "message": f"Received {tweets_stored} tweets (saved to database)",
                "status": "success"
            }
            
            logger.info(f"Successfully stored campaign batch {campaign_batch_id}: {tweets_stored} tweets")
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error in receive-tweets: {str(e)}")
            return Response({
                "campaign_batch": data.get('campaign_batch', 'unknown'),
                "message": f"Error storing tweets: {str(e)}",
                "status": "error"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ============================================================================
# AJAX API ENDPOINTS FOR FRONTEND INTERACTIONS
# ============================================================================

class TweetDetailAPIView(APIView):
    """
    Get detailed tweet information for modal display
    """
    authentication_classes = []
    permission_classes = []
    
    def get(self, request, tweet_id):
        try:
            tweet = get_object_or_404(SourceTweet, id=tweet_id)
            
            tweet_data = {
                'id': tweet.id,
                'tweet_id': tweet.tweet_id,
                'content': tweet.content,
                'url': tweet.url,
                'tweet_url': tweet.tweet_url,
                'likes': tweet.likes,
                'retweets': tweet.retweets,
                'replies': tweet.replies,
                'quotes': tweet.quotes,
                'views': tweet.views,
                'date': tweet.date.isoformat() if tweet.date else None,
                'status': tweet.status,
                'execution_id': tweet.execution_id,
                'source_url': tweet.source_url,
                'is_processed': tweet.is_processed,
                'processed_at': tweet.processed_at.isoformat() if tweet.processed_at else None,
            }
            
            return Response({
                'success': True,
                'tweet': tweet_data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error fetching tweet details: {str(e)}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@method_decorator(csrf_exempt, name='dispatch')
class DeleteTweetAPIView(APIView):
    """
    Delete a single tweet
    """
    authentication_classes = []
    permission_classes = []
    
    def delete(self, request, tweet_id):
        try:
            tweet = get_object_or_404(SourceTweet, id=tweet_id)
            tweet_id_text = tweet.tweet_id
            tweet.delete()
            
            logger.info(f"Tweet {tweet_id_text} deleted successfully")
            
            return Response({
                'success': True,
                'message': f'Tweet {tweet_id_text} deleted successfully'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error deleting tweet: {str(e)}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@method_decorator(csrf_exempt, name='dispatch')
class BulkDeleteTweetsAPIView(APIView):
    """
    Delete multiple tweets in bulk
    """
    authentication_classes = []
    permission_classes = []
    
    def delete(self, request):
        try:
            data = json.loads(request.body)
            tweet_ids = data.get('tweet_ids', [])
            
            if not tweet_ids:
                return Response({
                    'success': False,
                    'error': 'No tweet IDs provided'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get tweets to delete
            tweets_to_delete = SourceTweet.objects.filter(id__in=tweet_ids)
            deleted_count = tweets_to_delete.count()
            
            if deleted_count == 0:
                return Response({
                    'success': False,
                    'error': 'No tweets found with the provided IDs'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Delete tweets
            tweets_to_delete.delete()
            
            logger.info(f"Bulk deleted {deleted_count} tweets")
            
            return Response({
                'success': True,
                'message': f'Successfully deleted {deleted_count} tweets',
                'deleted_count': deleted_count
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error in bulk delete: {str(e)}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@method_decorator(csrf_exempt, name='dispatch')
class SaveGeneratedTweetAPIView(APIView):
    """
    Save changes to a generated tweet
    """
    authentication_classes = []
    permission_classes = []
    
    def post(self, request, tweet_id):
        try:
            tweet = get_object_or_404(GeneratedTweet, id=tweet_id)
            data = json.loads(request.body)
            
            # Update tweet content and metadata
            tweet.content = data.get('content', tweet.content)
            tweet.character_count = len(tweet.content)
            tweet.engagement_hook = data.get('engagement_hook', tweet.engagement_hook)
            tweet.save()
            
            logger.info(f"Generated tweet {tweet_id} saved successfully")
            
            return Response({
                'success': True,
                'message': 'Tweet saved successfully',
                'character_count': tweet.character_count
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error saving generated tweet: {str(e)}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@method_decorator(csrf_exempt, name='dispatch')
class ApproveGeneratedTweetAPIView(APIView):
    """
    Approve a generated tweet
    """
    authentication_classes = []
    permission_classes = []
    
    def post(self, request, tweet_id):
        try:
            tweet = get_object_or_404(GeneratedTweet, id=tweet_id)
            tweet.status = 'approved'
            tweet.save()
            
            logger.info(f"Generated tweet {tweet_id} approved")
            
            return Response({
                'success': True,
                'message': 'Tweet approved successfully'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error approving generated tweet: {str(e)}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@method_decorator(csrf_exempt, name='dispatch')
class RejectGeneratedTweetAPIView(APIView):
    """
    Reject a generated tweet
    """
    authentication_classes = []
    permission_classes = []
    
    def post(self, request, tweet_id):
        try:
            tweet = get_object_or_404(GeneratedTweet, id=tweet_id)
            tweet.status = 'rejected'
            tweet.save()
            
            logger.info(f"Generated tweet {tweet_id} rejected")
            
            return Response({
                'success': True,
                'message': 'Tweet rejected successfully'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error rejecting generated tweet: {str(e)}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@method_decorator(csrf_exempt, name='dispatch')
class DeleteGeneratedTweetAPIView(APIView):
    """
    Delete a generated tweet
    """
    authentication_classes = []
    permission_classes = []
    
    def delete(self, request, tweet_id):
        try:
            tweet = get_object_or_404(GeneratedTweet, id=tweet_id)
            tweet.delete()
            
            logger.info(f"Generated tweet {tweet_id} deleted")
            
            return Response({
                'success': True,
                'message': 'Tweet deleted successfully'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error deleting generated tweet: {str(e)}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@method_decorator(csrf_exempt, name='dispatch')
class PostTweetToXAPIView(APIView):
    """
    Post tweet to X.com (placeholder for now)
    """
    authentication_classes = []
    permission_classes = []
    
    def post(self, request, tweet_id):
        try:
            tweet = get_object_or_404(GeneratedTweet, id=tweet_id)
            
            # TODO: Implement actual X.com API integration
            # For now, just mark as posted
            tweet.status = 'posted'
            tweet.posted_at = timezone.now()
            tweet.save()
            
            logger.info(f"Generated tweet {tweet_id} marked as posted (placeholder)")
            
            return Response({
                'success': True,
                'message': 'Tweet posted successfully (placeholder)',
                'placeholder': True
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error posting generated tweet: {str(e)}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ============================================================================
# MAIN INTERFACE VIEWS
# ============================================================================

class ScrapedTweetsView(LoginRequiredMixin, TemplateView):
    """Scraped Tweets Database Interface - /twitter/sourcetweet/"""
    template_name = 'twitter/scraped_tweets.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get all source tweets as base queryset
        tweets = SourceTweet.objects.all()
        
        # Apply filters based on GET parameters
        filters = {}
        
        # Content search
        search_content = self.request.GET.get('search_content', '').strip()
        if search_content:
            tweets = tweets.filter(content__icontains=search_content)
            filters['search_content'] = search_content
        
        # Tweet ID search
        tweet_id_search = self.request.GET.get('tweet_id_search', '').strip()
        if tweet_id_search:
            tweets = tweets.filter(tweet_id__icontains=tweet_id_search)
            filters['tweet_id_search'] = tweet_id_search
        
        # Execution ID filter
        execution_filter = self.request.GET.get('execution_id', '').strip()
        if execution_filter:
            tweets = tweets.filter(execution_id__icontains=execution_filter)
            filters['execution_id'] = execution_filter
        
        # Date range filters
        date_from = self.request.GET.get('date_from')
        if date_from:
            tweets = tweets.filter(date__gte=date_from)
            filters['date_from'] = date_from
            
        date_to = self.request.GET.get('date_to')
        if date_to:
            from django.utils import timezone
            import datetime
            try:
                # Parse date and add time
                date_obj = datetime.datetime.strptime(date_to, '%Y-%m-%d')
                date_obj = date_obj.replace(hour=23, minute=59, second=59)
                tweets = tweets.filter(date__lte=date_obj)
                filters['date_to'] = date_to
            except ValueError:
                # Invalid date format, skip filter
                pass
        
        # Status filter
        status_filter = self.request.GET.get('status_filter', '').strip()
        if status_filter:
            tweets = tweets.filter(status=status_filter)
            filters['status_filter'] = status_filter
        
        # Engagement threshold filters
        min_likes = self.request.GET.get('min_likes')
        if min_likes and min_likes.isdigit():
            tweets = tweets.filter(likes__gte=int(min_likes))
            filters['min_likes'] = min_likes
            
        min_retweets = self.request.GET.get('min_retweets')
        if min_retweets and min_retweets.isdigit():
            tweets = tweets.filter(retweets__gte=int(min_retweets))
            filters['min_retweets'] = min_retweets
            
        min_views = self.request.GET.get('min_views')
        if min_views and min_views.isdigit():
            tweets = tweets.filter(views__gte=int(min_views))
            filters['min_views'] = min_views
        
        # Processed filter
        processed_filter = self.request.GET.get('processed_filter', '').strip()
        if processed_filter == 'true':
            tweets = tweets.filter(is_processed=True)
            filters['processed_filter'] = processed_filter
        elif processed_filter == 'false':
            tweets = tweets.filter(is_processed=False)
            filters['processed_filter'] = processed_filter
        
        # Sorting
        sort_by = self.request.GET.get('sort_by', '-date')
        if sort_by == '-total_engagement':
            # Calculate total engagement as sum of likes + retweets + replies + quotes
            tweets = tweets.annotate(
                total_engagement=models.F('likes') + models.F('retweets') + models.F('replies') + models.F('quotes')
            ).order_by('-total_engagement')
        elif sort_by in ['-date', 'date', '-likes', '-retweets', '-views']:
            tweets = tweets.order_by(sort_by)
        else:
            tweets = tweets.order_by('-date')  # Default sorting
        
        # Calculate statistics (before pagination)
        total_tweets = SourceTweet.objects.count()  # Total in database
        filtered_tweets_count = tweets.count()  # After filters
        
        # Calculate aggregated statistics for filtered results
        aggregated_stats = tweets.aggregate(
            total_likes=models.Sum('likes'),
            total_retweets=models.Sum('retweets'),
            total_views=models.Sum('views')
        )
        
        total_likes = aggregated_stats['total_likes'] or 0
        total_retweets = aggregated_stats['total_retweets'] or 0
        total_views = aggregated_stats['total_views'] or 0
        total_executions = tweets.values('execution_id').distinct().count()
        
        # Pagination
        page = self.request.GET.get('page', 1)
        per_page = 50  # Show 50 tweets per page
        
        from django.core.paginator import Paginator
        paginator = Paginator(tweets, per_page)
        tweets_page = paginator.get_page(page)
        
        # Get unique execution IDs for filter dropdown
        execution_ids = SourceTweet.objects.values_list('execution_id', flat=True).distinct().filter(execution_id__isnull=False)
        
        context.update({
            'tweets': tweets_page,
            'total_tweets': total_tweets,
            'filtered_tweets_count': filtered_tweets_count,
            'total_likes': total_likes,
            'total_retweets': total_retweets,
            'total_views': total_views,
            'total_executions': total_executions,
            'execution_ids': execution_ids,
            'current_execution_filter': execution_filter,
            'showing_start': tweets_page.start_index() if tweets_page else 0,
            'showing_end': tweets_page.end_index() if tweets_page else 0,
            'total_filtered': tweets_page.paginator.count if tweets_page else 0,
            'active_filters': filters,
        })
        
        return context

class ExportTweetsView(LoginRequiredMixin, View):
    """Export tweets to CSV - /twitter/sourcetweet/export/"""
    
    def get(self, request):
        import csv
        from django.http import HttpResponse
        
        # Get filter parameters
        execution_filter = request.GET.get('execution_id', '')
        export_type = request.GET.get('type', 'all')  # 'page' or 'all'
        
        # Get tweets based on filter
        tweets = SourceTweet.objects.all().order_by('-date')
        if execution_filter:
            tweets = tweets.filter(execution_id__icontains=execution_filter)
        
        # Create CSV response
        response = HttpResponse(content_type='text/csv')
        filename = f"scraped_tweets_{timezone.now().strftime('%Y%m%d_%H%M%S')}.csv"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        writer = csv.writer(response)
        
        # Write header
        writer.writerow([
            'Tweet ID', 'Content', 'URL', 'Likes', 'Retweets', 'Replies', 
            'Quotes', 'Views', 'Date', 'Execution ID', 'Status'
        ])
        
        # Write data
        for tweet in tweets:
            writer.writerow([
                tweet.tweet_id,
                tweet.content,
                tweet.url,
                tweet.likes,
                tweet.retweets,
                tweet.replies,
                tweet.quotes,
                tweet.views,
                tweet.date.strftime('%Y-%m-%d %H:%M:%S'),
                tweet.execution_id,
                tweet.status
            ])
        
        return response

class GenerateTweetsView(TemplateView):
    """Main dashboard showing all campaign batches - /generate-tweets/"""
    template_name = 'twitter/generate_tweets.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['campaign_batches'] = CampaignBatch.objects.all()
        return context

class CampaignReviewView(TemplateView):
    """Individual campaign review interface - /review/{batch}/"""
    template_name = 'twitter/campaign_review.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        batch_id = kwargs.get('campaign_batch')
        campaign_batch = get_object_or_404(CampaignBatch, batch_id=batch_id)
        
        # Calculate statistics
        tweets = campaign_batch.tweets.all()
        stats = {
            'total_tweets': tweets.count(),
            'draft': tweets.filter(status='Draft').count(),
            'approved': tweets.filter(status='Approved').count(),
            'posted': tweets.filter(status='Posted').count(),
            'rejected': tweets.filter(status='Rejected').count(),
            'deleted': tweets.filter(status='Deleted').count(),
        }
        
        context.update({
            'campaign_batch': campaign_batch,
            'tweets': tweets,
            'stats': stats
        })
        return context

# ============================================================================
# EXISTING DASHBOARD VIEW
# ============================================================================

@login_required
def dashboard(request):
    """Twitter dashboard view."""
    return render(request, 'twitter/dashboard.html', {
        'platform': 'Twitter',
        'platform_icon': '𝕏',
        'platform_color': '#1da1f2'
    })

# Placeholder views for URL patterns
@login_required
def post_list(request):
    return HttpResponse("Twitter posts - Coming soon!")

@login_required
def post_create(request):
    return HttpResponse("Create Twitter post - Coming soon!")

@login_required
def post_detail(request, pk):
    return HttpResponse(f"Twitter post {pk} - Coming soon!")

@login_required
def post_edit(request, pk):
    return HttpResponse(f"Edit Twitter post {pk} - Coming soon!")

@login_required
def post_delete(request, pk):
    return HttpResponse(f"Delete Twitter post {pk} - Coming soon!")

@login_required
def media_upload(request):
    return HttpResponse("Twitter media upload - Coming soon!")

@login_required
def media_delete(request, pk):
    return HttpResponse(f"Delete Twitter media {pk} - Coming soon!")

@login_required
def generate_preview(request):
    return HttpResponse("Twitter preview - Coming soon!")

@login_required
def schedule_tweet(request):
    return HttpResponse("Schedule tweet - Coming soon!")

@login_required
def post_tweet(request):
    return HttpResponse("Post tweet - Coming soon!")

@login_required
def analytics(request):
    return HttpResponse("Twitter analytics - Coming soon!")

@login_required
def export_analytics(request):
    return HttpResponse("Export Twitter analytics - Coming soon!")
