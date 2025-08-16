from django.test import TestCase
from django.utils import timezone
from linkedin.models import LinkedInPost
from core.models import Campaign

class LinkedInPostModelTests(TestCase):
    def setUp(self):
        """Set up test data."""
        self.campaign = Campaign.objects.create(
            name="LinkedIn Test Campaign",
            description="Test Description",
            platform="linkedin"
        )

    def test_linkedin_post_creation(self):
        """Test creating a LinkedIn post with basic attributes."""
        post = LinkedInPost.objects.create(
            campaign=self.campaign,
            content="Test LinkedIn post #innovation",
            status="draft",
            post_type="article"
        )
        self.assertEqual(post.content, "Test LinkedIn post #innovation")
        self.assertEqual(post.platform, "linkedin")
        self.assertEqual(post.status, "draft")
        self.assertEqual(post.post_type, "article")

    def test_linkedin_post_types(self):
        """Test different LinkedIn post types."""
        # Test article post
        article_post = LinkedInPost.objects.create(
            campaign=self.campaign,
            content="Article post",
            status="draft",
            post_type="article",
            article_url="https://example.com/article"
        )
        self.assertEqual(article_post.post_type, "article")
        self.assertEqual(article_post.article_url, "https://example.com/article")

        # Test document post
        document_post = LinkedInPost.objects.create(
            campaign=self.campaign,
            content="Document post",
            status="draft",
            post_type="document",
            document_title="Test Document"
        )
        self.assertEqual(document_post.post_type, "document")
        self.assertEqual(document_post.document_title, "Test Document")

    def test_linkedin_post_scheduling(self):
        """Test scheduling a LinkedIn post."""
        scheduled_time = timezone.now() + timezone.timedelta(days=1)
        post = LinkedInPost.objects.create(
            campaign=self.campaign,
            content="Scheduled LinkedIn post",
            status="scheduled",
            scheduled_time=scheduled_time,
            post_type="text"
        )
        self.assertEqual(post.status, "scheduled")
        self.assertEqual(post.scheduled_time, scheduled_time)

    def test_linkedin_media_attachment(self):
        """Test attaching media to a LinkedIn post."""
        post = LinkedInPost.objects.create(
            campaign=self.campaign,
            content="Post with media",
            status="draft",
            post_type="image"
        )
        # Add media asset
        media = post.add_media(
            file_type="image",
            file_url="https://example.com/image.jpg",
            title="Test Image",
            description="Image description"
        )
        self.assertEqual(media.title, "Test Image")
        self.assertEqual(media.description, "Image description")
        self.assertEqual(post.media_assets.count(), 1)

    def test_linkedin_hashtag_validation(self):
        """Test LinkedIn-specific hashtag validation."""
        # LinkedIn allows up to 3 hashtags per post
        post = LinkedInPost.objects.create(
            campaign=self.campaign,
            content="Test post #one #two #three #four",
            status="draft",
            post_type="text"
        )
        hashtags = post.get_hashtags()
        self.assertLessEqual(len(hashtags), 3, "LinkedIn posts should have 3 or fewer hashtags")
