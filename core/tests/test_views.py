from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from core.models import Campaign, Post
from rest_framework.test import APIClient
from rest_framework import status

class CampaignViewTests(TestCase):
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.campaign = Campaign.objects.create(
            name="Test Campaign",
            description="Test Description",
            platform="linkedin",
            status="draft"
        )

    def test_campaign_list_view(self):
        """Test retrieving a list of campaigns."""
        url = reverse('campaign-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], self.campaign.name)

    def test_campaign_detail_view(self):
        """Test retrieving a single campaign."""
        url = reverse('campaign-detail', args=[self.campaign.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.campaign.name)
        self.assertEqual(response.data['platform'], self.campaign.platform)

    def test_create_campaign(self):
        """Test creating a new campaign."""
        url = reverse('campaign-list')
        data = {
            'name': 'New Campaign',
            'description': 'New Description',
            'platform': 'twitter',
            'status': 'draft'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Campaign.objects.count(), 2)
        self.assertEqual(response.data['name'], 'New Campaign')

class PostViewTests(TestCase):
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.campaign = Campaign.objects.create(
            name="Test Campaign",
            platform="linkedin"
        )
        self.post = Post.objects.create(
            campaign=self.campaign,
            content="Test post content",
            platform="linkedin",
            status="draft"
        )

    def test_post_list_view(self):
        """Test retrieving a list of posts."""
        url = reverse('post-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['content'], self.post.content)

    def test_post_detail_view(self):
        """Test retrieving a single post."""
        url = reverse('post-detail', args=[self.post.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['content'], self.post.content)
        self.assertEqual(response.data['platform'], self.post.platform)

    def test_create_post(self):
        """Test creating a new post."""
        url = reverse('post-list')
        data = {
            'campaign': self.campaign.id,
            'content': 'New post content',
            'platform': 'twitter',
            'status': 'draft'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 2)
        self.assertEqual(response.data['content'], 'New post content')

    def test_update_post(self):
        """Test updating a post."""
        url = reverse('post-detail', args=[self.post.id])
        data = {
            'content': 'Updated content',
            'status': 'scheduled'
        }
        response = self.client.patch(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.post.refresh_from_db()
        self.assertEqual(self.post.content, 'Updated content')
        self.assertEqual(self.post.status, 'scheduled')
