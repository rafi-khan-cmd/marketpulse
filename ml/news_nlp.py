"""
NLP utilities for NewsArticle:
- sentiment (positive/negative/neutral + score)
- abstractive summary
- lightweight topic tagging (keyword-based to avoid huge models)
"""

import os

from django.db import transaction
from transformers import pipeline

from core.models import NewsArticle


# --- 1. Global pipeline objects (lazy-loaded) ------------------------------

# These start as None and are created on first use.
_sentiment_pipe = None
_summary_pipe = None

# Allow overriding via env vars in case we ever want to experiment without
# touching code. Using distilled models keeps memory usage low on Railway.
SENTIMENT_MODEL = os.getenv(
    "NEWS_SENTIMENT_MODEL",
    "distilbert/distilbert-base-uncased-finetuned-sst-2-english",
)
SUMMARY_MODEL = os.getenv(
    "NEWS_SUMMARY_MODEL",
    "sshleifer/distilbart-cnn-12-6",  # distilled BART (~300MB vs 1.6GB)
)


def get_pipelines():
    """
    Lazily initialize and return the NLP pipelines:

    - sentiment analysis (always used)
    - summarization (always used)

    Avoid loading massive zero-shot topic models to stay within
    Railway/Render free tier memory budgets.
    """
    global _sentiment_pipe, _summary_pipe

    # 1) Sentiment pipeline
    if _sentiment_pipe is None:
        _sentiment_pipe = pipeline("sentiment-analysis", model=SENTIMENT_MODEL)

    # 2) Summarization pipeline (distilled BART)
    if _summary_pipe is None:
        _summary_pipe = pipeline(
            "summarization",
            model=SUMMARY_MODEL,
            framework="pt",
        )

    return _sentiment_pipe, _summary_pipe


# --- 2. Topic inference via simple keyword rules ---------------------------

TOPIC_KEYWORDS = {
    "inflation": ["inflation", "cpi", "prices", "costs"],
    "interest rates": ["interest rate", "rate hike", "rate cut", "fed funds"],
    "jobs": ["employment", "jobless", "jobs report", "labor"],
    "earnings": ["earnings", "profits", "quarterly results"],
    "recession": ["recession", "slowdown", "contraction"],
    "growth": ["gdp", "growth", "expansion"],
    "stocks": ["stock", "equities", "market"],
    "bonds": ["bond", "treasury", "yield"],
    "central bank": ["federal reserve", "fed", "central bank"],
    "commodities": ["oil", "gold", "commodity", "energy"],
}


def infer_topics(text: str) -> str:
    """
    Very light-weight topic tagging that looks for keyword hits.
    Keeps resource usage near-zero compared to zero-shot models.
    """
    lower = text.lower()
    hits = []
    for topic, keywords in TOPIC_KEYWORDS.items():
        if any(keyword in lower for keyword in keywords):
            hits.append(topic)
    return ", ".join(sorted(set(hits)))


def annotate_article_text(text: str):
    """
    Given article text (title or raw_text), return:
    - sentiment_label  (e.g. 'POSITIVE', 'NEGATIVE', 'NEUTRAL')
    - sentiment_score  (float, confidence)
    - summary          (short abstractive summary)
    - topics_str       (comma-separated topics or '' if not available)
    """
    sentiment_pipe, summary_pipe = get_pipelines()

    # 1) Sentiment — truncate text to keep it cheap
    s_res = sentiment_pipe(text[:512])[0]
    sentiment_label = s_res["label"]
    sentiment_score = float(s_res["score"])

    # 2) Summary — distilled BART keeps memory modest while
    # still producing decent summaries.
    sum_res = summary_pipe(
        text,
        max_length=80,
        min_length=20,
        do_sample=False,
    )[0]["summary_text"]

    # 3) Topics — cheap keyword-based tags
    topics_str = infer_topics(text)

    return sentiment_label, sentiment_score, sum_res, topics_str


# --- 3. Main entry point: run NLP on NewsArticle rows ----------------------


def run_news_nlp(limit: int = 25):
    """
    Find NewsArticle rows that do not have sentiment yet,
    run NLP on them, and save the results.

    Usage from Django shell:

        >>> from ml.news_nlp import run_news_nlp
        >>> run_news_nlp(limit=10)
    """
    # Only process articles where sentiment_label is still empty string.
    qs = NewsArticle.objects.filter(
        sentiment_label="",
    ).order_by("-published_at")[:limit]

    # Convert to list to get actual count of limited results
    articles_list = list(qs)
    
    if not articles_list:
        print("No articles need NLP right now.")
        return

    print(f"Running NLP on {len(articles_list)} articles...")

    for art in articles_list:
        # If you later store full raw_text, use that; for now, title is fine.
        if art.raw_text:
            text = art.raw_text
        else:
            text = art.title

        try:
            (
                sentiment_label,
                sentiment_score,
                summary,
                topics_str,
            ) = annotate_article_text(text)
        except Exception as e:
            print(f"Error processing article {art.id}: {e}")
            continue

        # Save fields atomically for this article
        with transaction.atomic():
            art.sentiment_label = sentiment_label
            art.sentiment_score = sentiment_score
            art.summary = summary
            art.topics = topics_str
            art.save(
                update_fields=[
                    "sentiment_label",
                    "sentiment_score",
                    "summary",
                    "topics",
                ]
            )

            print(
                f"Updated article {art.id}: "
                f"{sentiment_label} ({sentiment_score:.2f}); topics={topics_str}"
            )

    print("Done NLP processing.")