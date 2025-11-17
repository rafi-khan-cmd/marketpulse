from django.test import TestCase
from datetime import date, timedelta
from unittest.mock import patch, MagicMock
import pandas as pd

from core.models import Series, Observation
from etl.features import get_series_value_on_or_before, build_features_for_date


class FeaturesTest(TestCase):
    """Test feature engineering functions."""
    
    def setUp(self):
        self.series = Series.objects.create(
            code="TEST_SERIES",
            name="Test Series",
            freq="D",
            source="TEST"
        )
        # Create some historical observations
        for i in range(5):
            Observation.objects.create(
                series=self.series,
                date=date.today() - timedelta(days=i),
                value=100.0 + i
            )
    
    def test_get_series_value_on_or_before(self):
        """Test getting series value on or before a date."""
        value = get_series_value_on_or_before("TEST_SERIES", date.today())
        self.assertEqual(value, 100.0)
        
        # Test with date in the past
        # Observations: today=100, today-1=101, today-2=102, today-3=103, today-4=104
        past_date = date.today() - timedelta(days=3)
        value = get_series_value_on_or_before("TEST_SERIES", past_date)
        self.assertEqual(value, 103.0)  # Should get the value for today-3
    
    def test_get_series_value_nonexistent(self):
        """Test getting value for non-existent series."""
        value = get_series_value_on_or_before("NONEXISTENT", date.today())
        self.assertIsNone(value)
    
    def test_build_features_for_date(self):
        """Test building features for a specific date."""
        # Create SPX series and observations
        spx_series = Series.objects.create(
            code="SPX_CLOSE",
            name="S&P 500",
            freq="D",
            source="YF"
        )
        Observation.objects.create(
            series=spx_series,
            date=date.today(),
            value=4500.0
        )
        Observation.objects.create(
            series=spx_series,
            date=date.today() - timedelta(days=1),
            value=4400.0
        )
        
        # Create VIX series
        vix_series = Series.objects.create(
            code="VIX",
            name="VIX",
            freq="D",
            source="YF"
        )
        Observation.objects.create(
            series=vix_series,
            date=date.today(),
            value=20.0
        )
        
        # Build features
        ff = build_features_for_date(date.today())
        
        self.assertIsNotNone(ff)
        self.assertEqual(ff.date, date.today())
        self.assertIn("spx_close", ff.features)
        self.assertIn("spx_ret_1d", ff.features)
        self.assertIn("vix_close", ff.features)


class MarketsETLTest(TestCase):
    """Test market ETL functionality."""
    
    @patch('etl.markets.yf.Ticker')
    def test_fetch_yf_history_success(self, mock_ticker):
        """Test successful yfinance data fetch."""
        # Mock yfinance response
        mock_df = pd.DataFrame({
            'Close': [4500.0, 4510.0],
            'Volume': [1000000, 1100000]
        }, index=pd.date_range('2024-01-01', periods=2))
        
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.history.return_value = mock_df
        mock_ticker.return_value = mock_ticker_instance
        
        from etl.markets import fetch_yf_history
        result = fetch_yf_history("SPY", period="1mo")
        
        self.assertFalse(result.empty)
        self.assertEqual(len(result), 2)
    
    @patch('etl.markets.yf.Ticker')
    def test_fetch_yf_history_failure(self, mock_ticker):
        """Test yfinance fetch failure handling."""
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.history.side_effect = Exception("API Error")
        mock_ticker.return_value = mock_ticker_instance
        
        from etl.markets import fetch_yf_history
        result = fetch_yf_history("INVALID", period="1mo")
        
        self.assertTrue(result.empty)
