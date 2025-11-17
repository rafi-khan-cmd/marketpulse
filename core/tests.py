from django.test import TestCase
from django.utils import timezone
from datetime import date, timedelta

from core.models import Series, Observation, NewsArticle, FeatureFrame


class SeriesModelTest(TestCase):
    """Test Series model functionality."""
    
    def setUp(self):
        self.series = Series.objects.create(
            code="TEST_SERIES",
            name="Test Series",
            freq="D",
            source="TEST"
        )
    
    def test_series_creation(self):
        """Test that a series can be created."""
        self.assertEqual(self.series.code, "TEST_SERIES")
        self.assertEqual(self.series.name, "Test Series")
    
    def test_series_str(self):
        """Test series string representation."""
        self.assertEqual(str(self.series), "TEST_SERIES")


class ObservationModelTest(TestCase):
    """Test Observation model functionality."""
    
    def setUp(self):
        self.series = Series.objects.create(
            code="TEST_SERIES",
            name="Test Series",
            freq="D",
            source="TEST"
        )
        self.observation = Observation.objects.create(
            series=self.series,
            date=date.today(),
            value=100.0
        )
    
    def test_observation_creation(self):
        """Test that an observation can be created."""
        self.assertEqual(self.observation.value, 100.0)
        self.assertEqual(self.observation.series, self.series)
    
    def test_unique_together_constraint(self):
        """Test that series and date combination is unique."""
        with self.assertRaises(Exception):
            Observation.objects.create(
                series=self.series,
                date=date.today(),
                value=200.0
            )


class NewsArticleModelTest(TestCase):
    """Test NewsArticle model functionality."""
    
    def setUp(self):
        self.article = NewsArticle.objects.create(
            source="Test Source",
            title="Test Article Title",
            url="https://example.com/article",
            published_at=timezone.now(),
            sentiment_label="POSITIVE",
            sentiment_score=0.95
        )
    
    def test_news_article_creation(self):
        """Test that a news article can be created."""
        self.assertEqual(self.article.title, "Test Article Title")
        self.assertEqual(self.article.sentiment_label, "POSITIVE")
        self.assertEqual(self.article.sentiment_score, 0.95)
    
    def test_news_article_str(self):
        """Test news article string representation."""
        self.assertIn("Test Source", str(self.article))
        self.assertIn("Test Article Title", str(self.article))


class FeatureFrameModelTest(TestCase):
    """Test FeatureFrame model functionality."""
    
    def setUp(self):
        self.feature_frame = FeatureFrame.objects.create(
            date=date.today(),
            features={
                "spx_close": 4500.0,
                "vix_close": 20.0,
                "cpi_level": 300.0
            },
            target=0.01,
            label=1
        )
    
    def test_feature_frame_creation(self):
        """Test that a feature frame can be created."""
        self.assertEqual(self.feature_frame.date, date.today())
        self.assertEqual(self.feature_frame.features["spx_close"], 4500.0)
        self.assertEqual(self.feature_frame.label, 1)
    
    def test_feature_frame_unique_date(self):
        """Test that date must be unique."""
        with self.assertRaises(Exception):
            FeatureFrame.objects.create(
                date=date.today(),
                features={}
            )


class TimeSeriesViewTest(TestCase):
    """Test TimeSeriesView API endpoint."""
    
    def setUp(self):
        from rest_framework.test import APIClient
        self.client = APIClient()
        self.series = Series.objects.create(
            code="TEST_SERIES",
            name="Test Series",
            freq="D",
            source="TEST"
        )
        Observation.objects.create(
            series=self.series,
            date=date.today(),
            value=100.0
        )
    
    def test_timeseries_endpoint_success(self):
        """Test successful time series retrieval."""
        response = self.client.get("/api/timeseries/?code=TEST_SERIES")
        self.assertEqual(response.status_code, 200)
        self.assertIn("data", response.data)
        self.assertEqual(len(response.data["data"]), 1)
    
    def test_timeseries_endpoint_missing_code(self):
        """Test time series endpoint with missing code parameter."""
        response = self.client.get("/api/timeseries/")
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.data)
    
    def test_timeseries_endpoint_invalid_code(self):
        """Test time series endpoint with invalid code."""
        response = self.client.get("/api/timeseries/?code=INVALID")
        self.assertEqual(response.status_code, 404)
        self.assertIn("error", response.data)
