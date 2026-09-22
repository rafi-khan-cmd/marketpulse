from datetime import date, timedelta
from typing import Dict, List, Optional

from django.db import transaction

from core.models import Series, Observation, FeatureFrame


def get_series_value_on_or_before(series_code: str, d: date) -> Optional[float]:
    try:
        series = Series.objects.get(code=series_code)
    except Series.DoesNotExist:
        return None

    obs = (
        Observation.objects
        .filter(series=series, date__lte=d)
        .order_by("-date")
        .first()
    )

    if obs is None:
        return None
    return obs.value


def build_features_for_date(
    d: date,
    prev_trading_day: Optional[date] = None,
    next_trading_day: Optional[date] = None,
) -> FeatureFrame:
    """
    Build (and persist) the FeatureFrame for a single trading day ``d``.

    ``prev_trading_day`` and ``next_trading_day`` are the actual adjacent
    trading days taken from the SPX series. When they are provided, the 1-day
    return and the direction label are computed against real trading days
    rather than calendar-adjacent dates (which, on a weekend, would compare a
    Friday close against itself and fabricate a zero-return / "down" label).

    If ``next_trading_day`` is None -- e.g. the most recent day, whose
    "tomorrow" has not happened yet -- the target and label are left unset
    (None) rather than being forced to zero.
    """
    features: Dict[str, float] = {}

    spx_today = get_series_value_on_or_before("SPX_CLOSE", d)

    if prev_trading_day is not None:
        spx_prev = get_series_value_on_or_before("SPX_CLOSE", prev_trading_day)
    else:
        spx_prev = get_series_value_on_or_before("SPX_CLOSE", d - timedelta(days=1))

    vix_today = get_series_value_on_or_before("VIX", d)
    spy_vol = get_series_value_on_or_before("SPY_VOLUME", d)

    if spx_today is not None:
        features["spx_close"] = spx_today
    if spx_today is not None and spx_prev is not None and spx_prev != 0:
        features["spx_ret_1d"] = (spx_today - spx_prev) / spx_prev
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

    # Direction target: next trading day's close vs. today's close. Only
    # computed when a following trading day actually exists.
    target: Optional[float] = None
    label: Optional[int] = None

    if next_trading_day is not None:
        spx_next = get_series_value_on_or_before("SPX_CLOSE", next_trading_day)
        if spx_today is not None and spx_next is not None and spx_today != 0:
            target = (spx_next - spx_today) / spx_today
            label = 1 if target > 0 else 0

    ff, __ = FeatureFrame.objects.update_or_create(
        date=d,
        defaults={
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

    # Only build features for days the market actually traded (days with an
    # SPX close). Iterating every calendar day would fabricate weekend rows
    # and mislabel Fridays, since a weekend "close" is just Friday's value.
    trading_days: List[date] = list(
        Observation.objects
        .filter(series=spx_series)
        .order_by("date")
        .values_list("date", flat=True)
    )

    if not trading_days:
        print("No SPX observations found.")
        return

    print(f"Building features from {trading_days[0]} to {trading_days[-1]} ...")

    with transaction.atomic():
        count = 0
        last_index = len(trading_days) - 1
        for i, d in enumerate(trading_days):
            prev_d = trading_days[i - 1] if i > 0 else None
            next_d = trading_days[i + 1] if i < last_index else None
            build_features_for_date(d, prev_d, next_d)
            count += 1

    print(f"Created/updated {count} FeatureFrame rows.")
