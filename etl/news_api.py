import os
from datetime import datetime

import requests
from django.conf import settings
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from core.models import NewsArticle


def _get_api_key():
    """
    Helper to retrieve the NewsAPI key.

    Checks:
    1) settings.NEWSAPI_KEY
    2) environment variable NEWSAPI_KEY

    If nothing is found, returns None and prints a message.
    """
    key = getattr(settings, "NEWSAPI_KEY", "") or os.getenv("NEWSAPI_KEY", "")
    if not key:
        print("NEWSAPI_KEY is missing. Set it in settings.py or as an environment variable.")
        return None
    return key


def _parse_published_at(published_at_str: str):
    """
    Convert NewsAPI's 'publishedAt' string (ISO format) into
    a timezone-aware datetime.

    Example input: '2025-11-15T12:34:56Z'
    """
    if not published_at_str:
        return timezone.now()

    # parse_datetime understands 'Z' (UTC) and returns an aware datetime or None
    dt = parse_datetime(published_at_str)
    if dt is None:
        # Fallback: try manual parsing and mark as UTC
        try:
            if published_at_str.endswith("Z"):
                published_at_str = published_at_str.replace("Z", "+00:00")
            dt = datetime.fromisoformat(published_at_str)
            if timezone.is_naive(dt):
                dt = timezone.make_aware(dt, timezone=timezone.utc)
        except Exception:
            dt = timezone.now()
    return dt


def run_news_etl_newsapi(page_size: int = 20):
    """
    Fetch latest business headlines from NewsAPI and store them in the database.

    Usage (from Django shell):

        >>> from etl.news_api import run_news_etl_newsapi
        >>> run_news_etl_newsapi()

    Steps:
    1. Call NewsAPI /top-headlines endpoint for 'business' category.
    2. For each article, upsert into NewsArticle (avoid duplicates by URL).
    """
    api_key = _get_api_key()
    if not api_key:
        return

    # NewsAPI endpoint for top business headlines (worldwide, English)
    url = "https://newsapi.org/v2/top-headlines"

    params = {
        "category": "business",
        "language": "en",
        "pageSize": page_size,
    }

    headers = {
        # NewsAPI supports "X-Api-Key" OR "Authorization: Bearer KEY".
        # We'll use X-Api-Key for simplicity.
        "X-Api-Key": api_key
    }

    print(f"Calling NewsAPI: {url} with params={params}")
    resp = requests.get(url, params=params, headers=headers)

    try:
        data = resp.json()
    except Exception as e:
        print("Failed to decode JSON from NewsAPI:", e)
        print("Raw response:", resp.text[:400])
        return

    # Basic error handling
    if resp.status_code != 200:
        print(f"NewsAPI returned status {resp.status_code}: {data}")
        return

    if data.get("status") != "ok":
        print("NewsAPI error response:", data)
        return

    articles = data.get("articles", [])
    print(f"Received {len(articles)} articles from NewsAPI.")

    inserted = 0

    for art in articles:
        title = (art.get("title") or "").strip()
        url = (art.get("url") or "").strip()
        source_name = (art.get("source", {}).get("name") or "Unknown").strip()
        published_at_str = art.get("publishedAt")
        content = art.get("content") or ""

        if not title or not url:
            # Skip malformed entries
            continue

        published_at = _parse_published_at(published_at_str)

        # Use URL as a unique key to avoid duplicates:
        obj, created = NewsArticle.objects.get_or_create(
            url=url,
            defaults={
                "source": source_name,
                "title": title,
                "published_at": published_at,
                # NLP fields left blank; will be filled by news_nlp
                "summary": "",
                "sentiment_label": "",
                "sentiment_score": None,
                "topics": "",
            },
        )

        if created:
            inserted += 1
            print(f"  + Inserted: [{source_name}] {title[:80]}")
        else:
            # Optional: could update title/published_at if needed
            pass

    print(f"Done. Inserted {inserted} new articles from NewsAPI.")