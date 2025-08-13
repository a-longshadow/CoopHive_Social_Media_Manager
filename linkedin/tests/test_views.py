from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from ..models import LinkedInPost
from core.models import Campaign

class LinkedInAPITests(TestCase):
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.campaign = Campaign.objects.create(
            name="LinkedIn Test Campaign",
            platform="linkedin"
        )
        
        self.post = LinkedInPost.objects.create(
            campaign=self.campaign,
            content="Test LinkedIn post #innovation",
            status="draft",
            post_type="article"
        )

    def test_list_linkedin_posts(self):
        """Test retrieving a list of LinkedIn posts."""
        url = reverse('linkedin-post-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['content'], self.post.content)

    def test_create_linkedin_post(self):
        """Test creating a new LinkedIn post."""
        url = reverse('linkedin-post-list')
        data = {
            'campaign': self.campaign.id,
            'content': 'New LinkedIn post #AI #Innovation',
            'status': 'draft',
            'post_type': 'article',
            'article_url': 'https://example.com/article'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(LinkedInPost.objects.count(), 2)
        self.assertEqual(response.data['content'], 'New LinkedIn post #AI #Innovation')
        self.assertEqual(response.data['post_type'], 'article')

    def test_schedule_linkedin_post(self):
        """Test scheduling a LinkedIn post."""
        url = reverse('linkedin-post-schedule', args=[self.post.id])
        scheduled_time = "2025-08-14T10:00:00Z"
        data = {'scheduled_time': scheduled_time}
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.post.refresh_from_db()
        self.assertEqual(self.post.status, 'scheduled')
        self.assertEqual(str(self.post.scheduled_time.isoformat()), scheduled_time)

    def test_linkedin_post_types(self):
        """Test creating different types of LinkedIn posts."""
        url = reverse('linkedin-post-list')
        
        # Test document post
        data = {
            'campaign': self.campaign.id,
            'content': 'Document post',
            'status': 'draft',
            'post_type': 'document',
            'document_title': 'Test Document',
            'document_url': 'https://example.com/document.pdf'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['post_type'], 'document')
        
        # Test image post
        data = {
            'campaign': self.campaign.id,
            'content': 'Image post',
            'status': 'draft',
            'post_type': 'image'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['post_type'], 'image')

    def test_linkedin_media_upload(self):
        """Test uploading media to a LinkedIn post."""
        url = reverse('linkedin-post-media', args=[self.post.id])
        data = {
            'file_type': 'image',
            'file_url': 'https://example.com/image.jpg',
            'title': 'Test Image',
            'description': 'Test image description'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.post.media_assets.count(), 1)
        self.assertEqual(self.post.media_assets.first().title, 'Test Image')
