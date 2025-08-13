from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from ..models import TwitterPost
from core.models import Campaign

class TwitterAPITests(TestCase):
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.campaign = Campaign.objects.create(
            name="Twitter Test Campaign",
            platform="twitter"
        )
        
        self.post = TwitterPost.objects.create(
            campaign=self.campaign,
            content="Test tweet #coophive",
            status="draft",
            character_count=len("Test tweet #coophive")
        )

    def test_list_twitter_posts(self):
        """Test retrieving a list of Twitter posts."""
        url = reverse('twitter-post-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['content'], self.post.content)

    def test_create_twitter_post(self):
        """Test creating a new Twitter post."""
        url = reverse('twitter-post-list')
        data = {
            'campaign': self.campaign.id,
            'content': 'New tweet #AI #Web3',
            'status': 'draft'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(TwitterPost.objects.count(), 2)
        self.assertEqual(response.data['content'], 'New tweet #AI #Web3')

    def test_schedule_twitter_post(self):
        """Test scheduling a Twitter post."""
        url = reverse('twitter-post-schedule', args=[self.post.id])
        scheduled_time = "2025-08-14T10:00:00Z"
        data = {'scheduled_time': scheduled_time}
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.post.refresh_from_db()
        self.assertEqual(self.post.status, 'scheduled')
        self.assertEqual(str(self.post.scheduled_time.isoformat()), scheduled_time)

    def test_twitter_post_validation(self):
        """Test Twitter post validation."""
        url = reverse('twitter-post-list')
        data = {
            'campaign': self.campaign.id,
            'content': 'x' * 281,  # Exceeds Twitter's 280 character limit
            'status': 'draft'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_twitter_media_upload(self):
        """Test uploading media to a Twitter post."""
        url = reverse('twitter-post-media', args=[self.post.id])
        data = {
            'file_type': 'image',
            'file_url': 'https://example.com/image.jpg',
            'alt_text': 'Test image'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.post.media_assets.count(), 1)
        self.assertEqual(self.post.media_assets.first().alt_text, 'Test image')
