from typing import List

import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib

from core.models import FeatureFrame

MODEL_PATH = "models/spx_direction_logreg.joblib"

def load_featureframe_as_dataframe() -> pd.DataFrame:
    qs = FeatureFrame.objects.exclude(label__isnull = True).order_by("date")

    records = []
    for ff in qs:
        row = {"date": ff.date, "label": ff.label}
        for k,v in ff.features.items():
            row[k] = v
        records.append(row)

    if not records:
        raise RuntimeError("No labeled FeatureFrame rows found.")

    df = pd.DataFrame.from_records(records)
    return df

def train_spx_direction_model() -> None:
    df = load_featureframe_as_dataframe()
    print("Loaded FeatureFrame data:", df.shape)

    feature_cols: List[str] = [
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

    df = df.dropna(subset = feature_cols + ["label"])
    print("After dropping NA:", df.shape)


    X = df[feature_cols].values
    y = df["label"].values

    # Use 20% for testing, ensuring we use all available data for training
    # For very large datasets, this gives us a substantial test set while maximizing training data
    test_size = 0.2
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=42, stratify=y
    )

    model = LogisticRegression(max_iter = 1000)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"Test accuracy: {acc:.3f}")

    joblib.dump(model, MODEL_PATH)
    print(f"Saved model to {MODEL_PATH}")