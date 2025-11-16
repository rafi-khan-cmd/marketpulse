from django.core.management.base import BaseCommand

from etl.fred import run_fred_etl
from etl.markets import run_markets_etl
from etl.features import build_features_for_all_dates

# 👇 IMPORTANT: use the NewsAPI-based ETL, not the RSS one
from etl.news_api import run_news_etl as run_newsapi_etl

from ml.train_spx_model import train_spx_direction_model
from ml.news_nlp import run_news_nlp


class Command(BaseCommand):
    """
    Update pipeline for MarketPulse.

    Steps:

    1. Refresh macro data from FRED.
    2. Refresh market data from yfinance.
    3. Rebuild the FeatureFrame table.
    4. Retrain the SPX direction model and save its artifact.
    5. Fetch latest news from NewsAPI and store them.
    6. Run NLP (sentiment, summary, topics) on the newest articles.
    """

    help = "Run all ETL + feature + model + news + NLP updates for MarketPulse."

    def handle(self, *args, **options):
        # 1) FRED macro ETL
        self.stdout.write(self.style.MIGRATE_HEADING("1) FRED macro ETL"))
        try:
            run_fred_etl()
            self.stdout.write(self.style.SUCCESS("   ✓ FRED ETL completed."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"   ✗ FRED ETL failed: {e}"))

        # 2) Market ETL (yfinance)
        self.stdout.write(self.style.MIGRATE_HEADING("2) Market ETL (yfinance)"))
        try:
            run_markets_etl()
            self.stdout.write(self.style.SUCCESS("   ✓ Market ETL completed."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"   ✗ Market ETL failed: {e}"))

        # 3) Build FeatureFrame
        self.stdout.write(self.style.MIGRATE_HEADING("3) Build FeatureFrame"))
        try:
            build_features_for_all_dates()
            self.stdout.write(self.style.SUCCESS("   ✓ Features built/updated."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"   ✗ Feature building failed: {e}"))

        # 4) Train SPX direction model
        self.stdout.write(self.style.MIGRATE_HEADING("4) Train SPX direction model"))
        try:
            train_spx_direction_model()
            self.stdout.write(self.style.SUCCESS("   ✓ Model trained and saved."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"   ✗ Model training failed: {e}"))

        # 5) News ETL (NewsAPI, from etl/news_api.py)
        self.stdout.write(self.style.MIGRATE_HEADING("5) News ETL (NewsAPI)"))
        try:
            # Call the NewsAPI ETL. Adjust arguments to match your news_api.run_news_etl signature.
            # Safe version: only pass limit.
            run_newsapi_etl(limit=25)
            self.stdout.write(self.style.SUCCESS("   ✓ News ETL completed."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"   ✗ News ETL failed: {e}"))

        # 6) News NLP (sentiment + topics)
        self.stdout.write(self.style.MIGRATE_HEADING("6) News NLP"))
        try:
            run_news_nlp(limit=50)
            self.stdout.write(self.style.SUCCESS("   ✓ News NLP completed."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"   ✗ News NLP failed: {e}"))

        self.stdout.write(self.style.SUCCESS("✅ MarketPulse update pipeline completed."))