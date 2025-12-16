from typing import List, Dict, Any
from datetime import date
import os

import numpy as np
from joblib import load

from core.models import FeatureFrame

# Use absolute path to ensure model is loaded correctly
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.path.join(BASE_DIR, "models")
MODEL_PATH = os.path.join(MODEL_DIR, "spx_direction_logreg.joblib")

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
    try:
        model = load(MODEL_PATH)
    except FileNotFoundError:
        raise RuntimeError(
            f"Model file not found at {MODEL_PATH}. Train the model first."
        )
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