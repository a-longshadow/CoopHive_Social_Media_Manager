from django.test import TestCase
from django.utils import timezone
from ..models import Campaign, Post, MediaAsset

class CampaignModelTests(TestCase):
    def test_campaign_creation(self):
        """Test creating a campaign with basic attributes."""
        campaign = Campaign.objects.create(
            name="Test Campaign",
            description="Test Description",
            platform="linkedin",
            status="draft"
        )
        self.assertEqual(campaign.name, "Test Campaign")
        self.assertEqual(campaign.platform, "linkedin")
        self.assertEqual(campaign.status, "draft")
        self.assertEqual(campaign.total_posts, 0)

    def test_campaign_str_representation(self):
        """Test the string representation of a Campaign."""
        campaign = Campaign.objects.create(
            name="Test Campaign",
            platform="twitter"
        )
        self.assertEqual(str(campaign), "Test Campaign (twitter)")

class PostModelTests(TestCase):
    def setUp(self):
        """Set up test data."""
        self.campaign = Campaign.objects.create(
            name="Test Campaign",
            platform="linkedin"
        )

    def test_post_creation(self):
        """Test creating a post with basic attributes."""
        post = Post.objects.create(
            campaign=self.campaign,
            content="Test post content",
            platform="linkedin",
            status="draft"
        )
        self.assertEqual(post.content, "Test post content")
        self.assertEqual(post.platform, "linkedin")
        self.assertEqual(post.status, "draft")
        self.assertIsNone(post.published_time)

    def test_post_scheduling(self):
        """Test scheduling a post."""
        scheduled_time = timezone.now() + timezone.timedelta(days=1)
        post = Post.objects.create(
            campaign=self.campaign,
            content="Scheduled post",
            platform="linkedin",
            status="scheduled",
            scheduled_time=scheduled_time
        )
        self.assertEqual(post.status, "scheduled")
        self.assertEqual(post.scheduled_time, scheduled_time)

class MediaAssetModelTests(TestCase):
    def setUp(self):
        """Set up test data."""
        self.campaign = Campaign.objects.create(
            name="Test Campaign",
            platform="linkedin"
        )
        self.post = Post.objects.create(
            campaign=self.campaign,
            content="Test post with media",
            platform="linkedin"
        )

    def test_media_asset_creation(self):
        """Test creating a media asset."""
        asset = MediaAsset.objects.create(
            post=self.post,
            file_type="image",
            file_url="https://example.com/image.jpg",
            original_filename="image.jpg"
        )
        self.assertEqual(asset.file_type, "image")
        self.assertEqual(asset.file_url, "https://example.com/image.jpg")
        self.assertEqual(str(asset), "image - image.jpg")
