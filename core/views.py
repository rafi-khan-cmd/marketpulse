from django.shortcuts import render  # optional, safe to keep
from django.views.generic import TemplateView
from datetime import timedelta

from rest_framework.views import APIView
from rest_framework.response import Response

from core.models import Series, Observation, NewsArticle, FeatureFrame
from ml.predict_spx import predict_latest_spx_direction
from django.core.management import call_command
from django.http import StreamingHttpResponse
import threading


class DashboardView(TemplateView):
    """
    Simple view that renders the MarketPulse dashboard HTML.
    """
    template_name = "core/dashboard.html"


class SPXDirectionView(APIView):
    """
    API endpoint that returns the latest SPX direction prediction.
    """
    def get(self, request, *args, **kwargs):
        result = predict_latest_spx_direction()
        return Response(result)


class TimeSeriesView(APIView):
    """
    Generic API endpoint to return a time series for a given Series.code.
    Example: /api/timeseries/?code=CPI or /api/timeseries/?code=SPX_CLOSE
    """

    def get(self, request, *args, **kwargs):
        # 1) Read the `code` query parameter from the URL
        code = request.query_params.get("code")

        # If no code is provided, return a 400 Bad Request with an error message
        if not code:
            return Response(
                {"error": "Missing 'code' query parameter, e.g. ?code=CPI"},
                status=400,
            )

        # 2) Look up the corresponding Series in the database
        try:
            series = Series.objects.get(code=code)
        except Series.DoesNotExist:
            return Response(
                {"error": f"Unknown series code '{code}'"},
                status=404,
            )

        # 3) Fetch all Observations for this series, ordered by date
        qs = Observation.objects.filter(series=series).order_by("date")

        # 4) Build a list of {date, value} dicts for the response
        data = [
            {"date": obs.date, "value": obs.value}
            for obs in qs
        ]

        # 5) Wrap everything in a structured JSON response
        result = {
            "code": series.code,
            # Use name if you have it; otherwise fall back to code
            "name": getattr(series, "name", series.code),
            "count": len(data),
            "data": data,
        }
        return Response(result)

def _get_series(code: str) -> Series:
    return Series.objects.get(code=code)


def _get_observation_on_or_before(code: str, target_date):
    """
    Return the latest Observation for `code` on or before `target_date`,
    or None if nothing exists.
    """
    series = _get_series(code)
    return (
        Observation.objects
        .filter(series=series, date__lte=target_date)
        .order_by("-date")
        .first()
    )


def _compute_cpi_yoy(feature_date):
    """
    Compute CPI year-over-year % using Observations:
    (CPI_today / CPI_1year_ago - 1) * 100
    """
    obs_now = _get_observation_on_or_before("CPI", feature_date)
    obs_year_ago = _get_observation_on_or_before("CPI", feature_date - timedelta(days=365))

    if not obs_now or not obs_year_ago or obs_year_ago.value == 0:
        return None

    return (obs_now.value / obs_year_ago.value - 1.0) * 100.0


def _compute_spx_drawdown(feature_date):
    """
    Compute drawdown at `feature_date`:
    (SPX_today - peak_so_far) / peak_so_far
    Negative -> below peak; 0 -> at peak.
    """
    series = _get_series("SPX_CLOSE")
    qs = Observation.objects.filter(series=series, date__lte=feature_date).order_by("date")
    if not qs.exists():
        return None

    peak = float("-inf")
    drawdown = None
    for obs in qs:
        if obs.value > peak:
            peak = obs.value
        dd = (obs.value - peak) / peak if peak != 0 else 0.0
        if obs.date == feature_date:
            drawdown = dd

    return drawdown


def _compute_macro_heat_index(snapshot: dict):
    """
    Simple composite score ~0–100:
    - Higher CPI YoY = hotter (above 2% target)
    - Lower unemployment = hotter
    - Steeper curve (10Y-2Y) = hotter
    """
    components = []

    cpi_yoy = snapshot.get("cpi_yoy")
    if cpi_yoy is not None:
        # 2% is 'neutral'; 6%+ very hot, 0% cold
        norm = (cpi_yoy - 2.0) / 4.0
        components.append(max(min(norm, 2.0), -2.0))

    unemp = snapshot.get("unemp_rate")
    if unemp is not None:
        # 4% is neutral; 3% very hot labour market, 7% cold
        norm = (4.0 - unemp) / 2.0
        components.append(max(min(norm, 2.0), -2.0))

    ts = snapshot.get("term_spread_10y_2y")
    if ts is not None:
        # Positive steep curve is hot; inverted curve is cold
        norm = ts * 5.0
        components.append(max(min(norm, 2.0), -2.0))

    if not components:
        return None, "Unknown"

    avg_norm = sum(components) / len(components)
    score = avg_norm * 50.0 + 50.0  # map [-2,2] → [0,100]

    if score >= 65:
        label = "Hot / late-cycle"
    elif score <= 35:
        label = "Cool / slowdown"
    else:
        label = "Neutral"

    return score, label


def _compute_risk_barometer(snapshot: dict):
    """
    Risk barometer ~0–100:
    Higher score = more stress / risk-off.
    Uses VIX and SPX drawdown.
    """
    base = 50.0
    vix = snapshot.get("vix")
    dd = snapshot.get("spx_drawdown")  # negative when below peak

    score = base

    if vix is not None:
        # Assume 20 is neutral. 30 = stressed, 15 = calm.
        score += max(min((vix - 20.0) / 2.0, 10.0), -10.0)

    if dd is not None:
        # dd is negative. -0.2 (–20%) = stressed.
        score += max(min(dd * -100.0 / 2.0, 10.0), -10.0)

    score = max(min(score, 100.0), 0.0)

    if score >= 65:
        label = "Stress / risk-off"
    elif score <= 35:
        label = "Calm / risk-on"
    else:
        label = "Normal"

    return score, label


class MacroSnapshotView(APIView):
    """
    Returns a one-row snapshot for the dashboard macro card.
    Pulls raw levels from FeatureFrame, then computes:
    - CPI YoY from Observations
    - SPX drawdown from Observations
    - Macro Heat Index
    - Risk Barometer
    """
    def get(self, request, *args, **kwargs):
        ff = FeatureFrame.objects.order_by("-date").first()
        if not ff:
            return Response({"detail": "No FeatureFrame data available."}, status=503)

        feats = ff.features or {}

        # Base values from FeatureFrame
        cpi_level = feats.get("cpi_level")
        unemp_rate = feats.get("unrate")
        us10y = feats.get("us10y")
        us2y = feats.get("us2y")
        term_spread = feats.get("term_spread_10y_2y")
        vix = feats.get("vix_close")
        spx_close = feats.get("spx_close")

        # Derived metrics from Observations
        cpi_yoy = _compute_cpi_yoy(ff.date)
        spx_drawdown = _compute_spx_drawdown(ff.date)

        snapshot = {
            "as_of": ff.date.isoformat(),
            "cpi_yoy": cpi_yoy,
            "cpi_level": cpi_level,
            "unemp_rate": unemp_rate,
            "us10y": us10y,
            "us2y": us2y,
            "term_spread_10y_2y": term_spread,
            "vix": vix,
            "spx_close": spx_close,
            "spx_drawdown": spx_drawdown,
            "regime_label": feats.get("regime_label"),  # optional, may be None
        }

        # Composite indices
        heat_score, heat_label = _compute_macro_heat_index(snapshot)
        risk_score, risk_label = _compute_risk_barometer(snapshot)

        snapshot["macro_heat_index"] = heat_score
        snapshot["macro_heat_label"] = heat_label
        snapshot["risk_barometer_score"] = risk_score
        snapshot["risk_barometer_label"] = risk_label

        return Response(snapshot)

class NewsListView(APIView):
    """
    Simple API endpoint that returns the latest news articles
    (with sentiment, summary, topics) for the dashboard.
    """
    def get(self, request, *args, **kwargs):
        # 1) Read ?limit= from the query string, default to 20 if missing
        try:
            limit = int(request.GET.get("limit", 20))
        except ValueError:
            limit = 20

        # 2) Query the latest news articles by published_at
        qs = NewsArticle.objects.order_by("-published_at")[:limit]

        # 3) Build a list of plain dicts that can be serialized as JSON
        articles_data = []
        for art in qs:
            articles_data.append(
                {
                    "source": art.source,
                    "title": art.title,
                    "url": art.url,
                    "published_at": art.published_at.isoformat(),
                    "summary": art.summary,
                    "sentiment_label": art.sentiment_label,
                    "sentiment_score": art.sentiment_score,
                    "topics": art.topics,
                }
            )

        # 4) Wrap it in a top-level object and return as JSON
        return Response(
            {
                "count": qs.count(),
                "articles": articles_data,
            }
        )


class MigrateView(APIView):
    """
    Endpoint to run database migrations. Visit this first!
    """
    def get(self, request, *args, **kwargs):
        try:
            call_command('migrate', verbosity=0)
            return Response({
                "status": "success",
                "message": "Migrations completed successfully!"
            })
        except Exception as e:
            return Response({
                "status": "error",
                "message": f"Migration failed: {str(e)}"
            }, status=500)


class UpdateDataView(APIView):
    """
    Simple endpoint to trigger data update. Just visit this URL in your browser!
    """
    def get(self, request, *args, **kwargs):
        import os
        import logging
        
        # Set up logging to stdout so it appears in Railway logs
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)
        
        # Check environment variables first
        missing_vars = []
        if not os.getenv("FRED_API_KEY"):
            missing_vars.append("FRED_API_KEY")
        if not os.getenv("DATABASE_URL"):
            missing_vars.append("DATABASE_URL")
        
        if missing_vars:
            logger.error(f"Missing environment variables: {', '.join(missing_vars)}")
            return Response({
                "status": "error",
                "message": f"Missing environment variables: {', '.join(missing_vars)}. Check Railway Variables tab.",
                "missing": missing_vars
            }, status=400)
        
        def run_update():
            try:
                logger.info("=" * 60)
                logger.info("STARTING MarketPulse Update")
                logger.info("=" * 60)
                logger.info(f"FRED_API_KEY: {'SET' if os.getenv('FRED_API_KEY') else 'MISSING'}")
                logger.info(f"NEWSAPI_KEY: {'SET' if os.getenv('NEWSAPI_KEY') else 'MISSING (optional)'}")
                logger.info(f"DATABASE_URL: {'SET' if os.getenv('DATABASE_URL') else 'MISSING'}")
                
                # Run the command with verbose output
                call_command('update_marketpulse', verbosity=2)
                
                logger.info("=" * 60)
                logger.info("MarketPulse Update COMPLETED")
                logger.info("=" * 60)
            except Exception as e:
                logger.error("=" * 60)
                logger.error("MarketPulse Update FAILED")
                logger.error("=" * 60)
                logger.error(f"Error: {str(e)}")
                import traceback
                logger.error(traceback.format_exc())
        
        # Run in background thread so it doesn't timeout
        thread = threading.Thread(target=run_update)
        thread.daemon = False  # Don't kill on main thread exit
        thread.start()
        
        return Response({
            "status": "started",
            "message": "Data update started in background. Check Railway logs (Deployments → View Logs) to see progress. This will take 5-15 minutes.",
            "check_logs": "Railway Dashboard → Your Service → Deployments → View Logs"
        })

# Helper functions for composite macro metrics
def _compute_macro_heat_index(snapshot: dict) -> tuple[float | None, str]:
    """
    Returns (score_0_100, label) for the Macro Heat Index.

    Uses:
      - CPI YoY (snapshot["cpi_yoy"])
      - Unemployment rate (snapshot["unemp_rate"])
      - Term spread (10Y-2Y) from snapshot["us10y"] - snapshot["us2y"]

    Score is just a simple, hand-crafted scaling for this project.
    """
    cpi = snapshot.get("cpi_yoy")
    unemp = snapshot.get("unemp_rate")
    us10y = snapshot.get("us10y")
    us2y = snapshot.get("us2y")

    if cpi is None or unemp is None or us10y is None or us2y is None:
        return None, "Unknown"

    term_spread = us10y - us2y  # >0 = steep, <0 = inverted

    # Rough normalization to [0, 1] for each component.
    # These ranges are arbitrary and just for demonstration.
    cpi_norm = min(max((cpi - 2.0) / (8.0 - 2.0), 0.0), 1.0)       # 2–8% range
    unemp_norm = min(max((unemp - 3.0) / (10.0 - 3.0), 0.0), 1.0)  # 3–10% range

    # If curve is inverted (negative), it increases heat.
    # Map term_spread from [-1.5, +2.0] → [0, 1], then flip so more inversion = hotter.
    spread_raw = max(min(term_spread, 2.0), -1.5)
    spread_norm = (spread_raw + 1.5) / (2.0 + 1.5)  # -> 0..1
    curve_heat = 1.0 - spread_norm  # inverted → close to 1

    # Weighted average
    score_0_1 = 0.45 * cpi_norm + 0.35 * unemp_norm + 0.20 * curve_heat
    score = round(score_0_1 * 100.0, 1)

    # Label buckets
    if score < 40:
        label = "Cool / Benign"
    elif score < 70:
        label = "Neutral / Watch"
    else:
        label = "Hot / Stressed"

    return score, label


def _compute_risk_barometer(snapshot: dict) -> tuple[float | None, str]:
    """
    Returns (score_0_100, label) for a simple Risk Barometer.

    Uses:
      - VIX level (snapshot["vix"])
      - SPX drawdown (snapshot["spx_drawdown"], negative = below high)

    Higher = more risk / more stress.
    """
    vix = snapshot.get("vix")
    drawdown = snapshot.get("spx_drawdown")  # e.g. -0.15 for -15%

    if vix is None or drawdown is None:
        return None, "Unknown"

    # Normalize VIX from [10, 40] → [0, 1]
    vix_clamped = max(min(vix, 40.0), 10.0)
    vix_norm = (vix_clamped - 10.0) / (40.0 - 10.0)

    # Normalize drawdown from [0, -0.5] → [0, 1]
    dd_clamped = max(min(drawdown, 0.0), -0.5)
    dd_norm = abs(dd_clamped) / 0.5

    # Weighted average: more weight on drawdown
    score_0_1 = 0.6 * dd_norm + 0.4 * vix_norm
    score = round(score_0_1 * 100.0, 1)

    if score < 30:
        label = "Calm"
    elif score < 60:
        label = "Cautious"
    else:
        label = "Stressed / High Risk"

    return score, label