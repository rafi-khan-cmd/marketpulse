from typing import List, Dict, Any
from datetime import date
from io import BytesIO

import numpy as np
import joblib

from core.models import FeatureFrame, ModelArtifact

# Model is now stored in database, no file path needed

FEATURE_COLS: List[str] = [
    "spx_close",
    "spx_ret_1d",
    "vix_close",
    "spy_volume",
    "cpi_level",
    "unrate",
    "us10y",
    "us2y",
    "term_spread_10y_2y",
]

def get_latest_feature_row() -> FeatureFrame:
    ff = FeatureFrame.objects.order_by("-date").first()
    if ff is None:
        raise RuntimeError("No FeatureFrame rows found. Run feature ETL first.")

    return ff

def extract_feature_vector(ff: FeatureFrame) -> np.ndarray:
    features_dict = ff.features
    values: List[float] = []
    for col in FEATURE_COLS:
        val = features_dict.get(col)
        if val is None:
            raise RuntimeError(f"Missing feature '{col}' for data {ff.date}")
        values.append(float(val))
    return np.array(values, dtype=float).reshape(1,-1)

def load_model():
    # Load latest model from database
    artifact = ModelArtifact.objects.filter(name="spx_direction_logreg").order_by("-created_at").first()
    if artifact is None:
        raise RuntimeError("No model artifact found in database. Train the model first.")
    
    # Use BytesIO to deserialize model from bytes
    buffer = BytesIO(artifact.data)
    model = joblib.load(buffer)
    buffer.close()
    return model

def predict_latest_spx_direction() -> Dict[str, Any]:
    ff = get_latest_feature_row()
    X = extract_feature_vector(ff)
    model = load_model()

    proba = model.predict_proba(X)[0,1]
    label = int(model.predict(X)[0])

    result: Dict[str, Any] = {
        "date": ff.date,
        "prob_up": float(proba),
        "label": label,
        "features": ff.features,
    }
    return result