from django.test import TestCase
from django.utils import timezone
from twitter.models import TwitterPost
from core.models import Campaign

class TwitterPostModelTests(TestCase):
    def setUp(self):
        """Set up test data."""
        self.campaign = Campaign.objects.create(
            name="Twitter Test Campaign",
            description="Test Description",
            platform="twitter"
        )

    def test_twitter_post_creation(self):
        """Test creating a Twitter post with basic attributes."""
        post = TwitterPost.objects.create(
            campaign=self.campaign,
            content="Test tweet content #coophive",
            status="draft",
            character_count=len("Test tweet content #coophive")
        )
        self.assertEqual(post.content, "Test tweet content #coophive")
        self.assertEqual(post.platform, "twitter")
        self.assertEqual(post.status, "draft")
        self.assertEqual(post.character_count, len("Test tweet content #coophive"))

    def test_twitter_post_validation(self):
        """Test Twitter-specific validation rules."""
        # Test character limit (280 chars for Twitter)
        long_content = "x" * 281
        with self.assertRaises(Exception):
            TwitterPost.objects.create(
                campaign=self.campaign,
                content=long_content,
                status="draft",
                character_count=len(long_content)
            )

    def test_twitter_hashtag_extraction(self):
        """Test extracting hashtags from content."""
        post = TwitterPost.objects.create(
            campaign=self.campaign,
            content="Test #AI #Web3 content",
            status="draft",
            character_count=len("Test #AI #Web3 content")
        )
        self.assertEqual(post.get_hashtags(), ["#AI", "#Web3"])

    def test_twitter_post_scheduling(self):
        """Test scheduling a Twitter post."""
        scheduled_time = timezone.now() + timezone.timedelta(days=1)
        post = TwitterPost.objects.create(
            campaign=self.campaign,
            content="Scheduled tweet",
            status="scheduled",
            scheduled_time=scheduled_time,
            character_count=len("Scheduled tweet")
        )
        self.assertEqual(post.status, "scheduled")
        self.assertEqual(post.scheduled_time, scheduled_time)

    def test_twitter_media_attachment(self):
        """Test attaching media to a Twitter post."""
        post = TwitterPost.objects.create(
            campaign=self.campaign,
            content="Tweet with media",
            status="draft",
            character_count=len("Tweet with media")
        )
        # Add media asset
        media = post.add_media(
            file_type="image",
            file_url="https://example.com/image.jpg",
            alt_text="Test image"
        )
        self.assertTrue(media.alt_text == "Test image")
        self.assertEqual(post.media_assets.count(), 1)
