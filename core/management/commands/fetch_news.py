from django.core.management.base import BaseCommand

from etl.news_api import run_news_etl_newsapi
from ml.news_nlp import run_news_nlp
from core.models import NewsArticle


class Command(BaseCommand):
    """
    This class defines a custom Django management command called `fetch_news`.

    When you run:
        python manage.py fetch_news

    Django finds this Command class and calls its `handle()` method.
    """

    # Short description shown in `python manage.py help`
    help = "Fetch latest business news from NewsAPI and run NLP (sentiment, summary, topics)."

    def add_arguments(self, parser):
        """
        Define optional CLI flags for the command, e.g.:

            --page-size 30
            --limit 50
            --skip-nlp

        Intention:
        - Give you flexibility without editing code each time.
        """
        parser.add_argument(
            "--page-size",
            type=int,
            default=20,
            help="How many headlines to request from NewsAPI (default: 20).",
        )

        parser.add_argument(
            "--limit",
            type=int,
            default=30,
            help="How many of the latest articles to run NLP on (default: 30).",
        )

        parser.add_argument(
            "--skip-nlp",
            action="store_true",
            help="If set, only fetch news from NewsAPI and skip the NLP step.",
        )

    def handle(self, *args, **options):
        """
        The main entry point for the command.
        Django calls this method when you run `python manage.py fetch_news`.

        Intention:
        1. Fetch fresh articles using NewsAPI ETL.
        2. Show how many are in the DB.
        3. Optionally run NLP (sentiment, summary, topics) on the latest ones.
        """
        page_size = options["page_size"]
        limit = options["limit"]
        skip_nlp = options["skip_nlp"]

        # Step 1: Fetch news from NewsAPI
        self.stdout.write(
            self.style.MIGRATE_HEADING(
                f"Step 1/2: Fetching news from NewsAPI (page_size={page_size})..."
            )
        )

        run_news_etl_newsapi(page_size=page_size)

        total = NewsArticle.objects.count()
        self.stdout.write(
            self.style.SUCCESS(f"News ETL complete. Total articles in DB: {total}")
        )

        # If user only wants ETL and no NLP, stop here
        if skip_nlp:
            self.stdout.write(
                self.style.WARNING("Skipping NLP step because --skip-nlp was provided.")
            )
            return

        # Step 2: Run NLP on the latest N articles
        self.stdout.write(
            self.style.MIGRATE_HEADING(
                f"Step 2/2: Running NLP (sentiment, summary, topics) on latest {limit} articles..."
            )
        )

        run_news_nlp(limit=limit)

        # Optional: show a quick preview of a few newest articles
        latest = (
            NewsArticle.objects.order_by("-published_at")[:5]
            .values("source", "title", "sentiment_label", "sentiment_score", "topics")
        )

        self.stdout.write(self.style.SUCCESS("NLP step complete. Sample of latest 5:"))
        for art in latest:
            self.stdout.write(
                f"  - [{art['source']}] {art['title'][:70]} "
                f"({art['sentiment_label']} {art['sentiment_score']:.2f}) "
                f"topics={art['topics']}"
            )

        self.stdout.write(
            self.style.SUCCESS("All done. News + NLP refresh is complete ✅")
        )