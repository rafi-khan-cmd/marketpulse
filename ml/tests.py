from django.test import TestCase
from datetime import date, timedelta
import numpy as np
from unittest.mock import patch, MagicMock

from core.models import FeatureFrame


class MLPredictionTest(TestCase):
    """Test ML prediction functionality."""
    
    def setUp(self):
        # Create a feature frame for testing
        self.feature_frame = FeatureFrame.objects.create(
            date=date.today(),
            features={
                "spx_close": 4500.0,
                "spx_ret_1d": 0.01,
                "vix_close": 20.0,
                "spy_volume": 1000000,
                "cpi_level": 300.0,
                "unrate": 3.5,
                "us10y": 4.5,
                "us2y": 4.0,
                "term_spread_10y_2y": 0.5
            },
            target=0.01,
            label=1
        )
    
    @patch('ml.predict_spx.load')
    @patch('ml.predict_spx.FeatureFrame')
    def test_predict_latest_spx_direction(self, mock_featureframe, mock_load):
        """Test SPX direction prediction."""
        # Mock the model
        mock_model = MagicMock()
        mock_model.predict_proba.return_value = np.array([[0.3, 0.7]])
        mock_model.predict.return_value = np.array([1])
        mock_load.return_value = mock_model
        
        # Mock FeatureFrame query
        mock_featureframe.objects.order_by.return_value.first.return_value = self.feature_frame
        
        from ml.predict_spx import predict_latest_spx_direction
        
        result = predict_latest_spx_direction()
        
        self.assertIn("date", result)
        self.assertIn("prob_up", result)
        self.assertIn("label", result)
        self.assertEqual(result["label"], 1)
        self.assertGreater(result["prob_up"], 0.5)
    
    def test_train_spx_model(self):
        """Test model training functionality."""
        # Delete the feature frame from setUp to avoid conflicts
        FeatureFrame.objects.all().delete()
        
        # Create multiple feature frames with labels (starting from yesterday to avoid conflict)
        for i in range(10):
            FeatureFrame.objects.create(
                date=date.today() - timedelta(days=i+1),  # Start from yesterday
                features={
                    "spx_close": 4500.0 + i,
                    "spx_ret_1d": 0.01,
                    "vix_close": 20.0,
                    "spy_volume": 1000000,
                    "cpi_level": 300.0,
                    "unrate": 3.5,
                    "us10y": 4.5,
                    "us2y": 4.0,
                    "term_spread_10y_2y": 0.5
                },
                target=0.01 if i % 2 == 0 else -0.01,
                label=1 if i % 2 == 0 else 0
            )
        
        from ml.train_spx_model import load_featureframe_as_dataframe
        
        df = load_featureframe_as_dataframe()
        
        self.assertGreater(len(df), 0)
        self.assertIn("label", df.columns)
        self.assertIn("spx_close", df.columns)

