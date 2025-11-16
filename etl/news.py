import datetime

import feedparser
from django.utils import timezone

from core.models import NewsArticle


# Try a few different feeds. If your network blocks some, at least one should work.
NEWS_FEEDS = [
    {
        "source": "BBC Business",
        "url": "http://feeds.bbci.co.uk/news/business/rss.xml",
    },
    {
        "source": "Yahoo Finance",
        "url": "https://finance.yahoo.com/news/rssindex",
    },
    {
        "source": "MarketWatch",
        "url": "https://feeds.marketwatch.com/marketwatch/topstories/",
    },
]


def parse_published(entry):
    """
    Convert RSS 'published' into a timezone-aware datetime.
    If parsing fails, fall back to timezone.now().
    """
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        dt = datetime.datetime(
            entry.published_parsed.tm_year,
            entry.published_parsed.tm_mon,
            entry.published_parsed.tm_mday,
            entry.published_parsed.tm_hour,
            entry.published_parsed.tm_min,
            entry.published_parsed.tm_sec,
        )
        return timezone.make_aware(dt)
    return timezone.now()


def upsert_article(source, title, url, published_at):
    """
    Insert the article if it doesn't exist yet (same source + url).
    """
    obj, created = NewsArticle.objects.get_or_create(
        source=source,
        url=url,
        defaults={
            "title": title,
            "published_at": published_at,
        },
    )
    return created


def run_news_etl(max_per_feed=20):
    """
    Fetch latest headlines from each RSS feed and store them in the database.

    Usage from Django shell:
        >>> from etl.news import run_news_etl
        >>> run_news_etl()
    """
    total_new = 0

    for feed in NEWS_FEEDS:
        src = feed["source"]
        url = feed["url"]
        print(f"Fetching feed: {src} ({url})")

        parsed = feedparser.parse(url)
        print(f"  -> bozo={parsed.bozo}, entries={len(parsed.entries)}")

        if parsed.bozo:
            print(f"  -> bozo_exception={parsed.bozo_exception}")

        entries = parsed.entries[:max_per_feed]

        for entry in entries:
            title = getattr(entry, "title", "").strip()
            link = getattr(entry, "link", "").strip()
            if not title or not link:
                print("  ! Skipping entry with missing title/link")
                continue

            published_at = parse_published(entry)
            created = upsert_article(src, title, link, published_at)
            if created:
                total_new += 1
                print(f"  + {title[:80]}")

    print(f"Done. Inserted {total_new} new articles.")