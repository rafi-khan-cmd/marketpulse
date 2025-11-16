from datetime import date, timedelta

from typing import Dict, Optional

from django.db import transaction

from core.models import Series, Observation, FeatureFrame

def get_series_value_on_or_before(series_code: str, d: date) -> Optional[float]:
    try:
        series = Series.objects.get(code=series_code)
    except:
        return None

    obs = (
        Observation.objects
        .filter(series=series, date__lte = d)
        .order_by("-date")
        .first()
    )

    if obs is None:
        return None
    return obs.value

def build_features_for_date(d: date) -> FeatureFrame:
    features: Dict[str, float] = {}

    spx_today = get_series_value_on_or_before("SPX_CLOSE", d)
    spx_yest = get_series_value_on_or_before("SPX_CLOSE", d - timedelta(days=1))
    vix_today = get_series_value_on_or_before("VIX", d)
    spy_vol = get_series_value_on_or_before("SPY_VOLUME", d)


    if spx_today is not None:
        features["spx_close"] = spx_today
    if spx_today is not None and spx_yest is not None and spx_yest != 0:
        features["spx_ret_1d"] = (spx_today - spx_yest) / spx_yest
    if vix_today is not None:
        features["vix_close"] = vix_today
    if spy_vol is not None:
        features["spy_volume"] = spy_vol

    cpi = get_series_value_on_or_before("CPI", d)
    unrate = get_series_value_on_or_before("Unemployment", d)
    us10y = get_series_value_on_or_before("US10Y", d)
    us2y = get_series_value_on_or_before("US2Y", d)

    if cpi is not None:
        features["cpi_level"] = cpi
    if unrate is not None:
        features["unrate"] = unrate
    if us10y is not None:
        features["us10y"] = us10y
    if us2y is not None:
        features["us2y"] = us2y
    if us10y is not None and us2y is not None:
        features["term_spread_10y_2y"] = us10y - us2y

    spx_tomorrow = get_series_value_on_or_before("SPX_CLOSE", d + timedelta(days=1))
    target: Optional[float] = None
    label: Optional[int] = None

    if spx_today is not None and spx_tomorrow is not None and spx_today != 0:
        target = (spx_tomorrow - spx_today) / spx_today
        label = 1 if target > 0 else 0

    ff, __ = FeatureFrame.objects.update_or_create(
        date = d,
        defaults = {
            "features": features,
            "target": target,
            "label": label,
        },
    )
    return ff

def build_features_for_all_dates() -> None:
    try:
        spx_series = Series.objects.get(code="SPX_CLOSE")
    except Series.DoesNotExist:
        print("No SPX_CLOSE series found. Run markets ETL first.")
        return

    qs = Observation.objects.filter(series=spx_series).order_by("date")
    if not qs.exists():
        print("No SPX observations found.")
        return

    start_date = qs.first().date
    end_date = qs.last().date

    print(f"Building features from {start_date} to {end_date} ...")

    with transaction.atomic():
        d = start_date
        count = 0
        while d <= end_date:
            build_features_for_date(d)
            count = count + 1
            d = d + timedelta(days = 1)

    print(f"Created/updated {count} FeatureFrame rows.")
