"""
NLP utilities for NewsArticle:
- sentiment (positive/negative/neutral + score)
- abstractive summary
- optional topic tags (zero-shot, if model can be loaded)
"""

from django.db import transaction
from transformers import pipeline

from core.models import NewsArticle


# --- 1. Global pipeline objects (lazy-loaded) ------------------------------

# These start as None and are created on first use.
_sentiment_pipe = None
_summary_pipe = None
_zs_pipe = None  # zero-shot (topics), optional


def get_pipelines():
    """
    Lazily initialize and return the NLP pipelines:

    - sentiment analysis (always used)
    - summarization (always used)
    - zero-shot classification (for topics, OPTIONAL)

    If the zero-shot model cannot be loaded (e.g., no internet,
    blocked HF, etc.), we set _zs_pipe = None and continue.
    """
    global _sentiment_pipe, _summary_pipe, _zs_pipe

    # 1) Sentiment pipeline
    if _sentiment_pipe is None:
        # Uses a default sentiment model: distilbert-base-uncased-finetuned-sst-2-english
        _sentiment_pipe = pipeline("sentiment-analysis")

    # 2) Summarization pipeline
    if _summary_pipe is None:
        # BART CNN summarization model (large but good quality)
        _summary_pipe = pipeline("summarization", model="facebook/bart-large-cnn")

    # 3) Zero-shot (topics) pipeline — OPTIONAL
    if _zs_pipe is None:
        try:
            _zs_pipe = pipeline(
                "zero-shot-classification",
                model="facebook/bart-large-mnli",
            )
        except Exception as e:
            # IMPORTANT: Do NOT crash the whole NLP step because topics failed.
            print(
                "Could not load zero-shot topics model. "
                "Topics will be left empty. Reason:", e
            )
            _zs_pipe = None

    return _sentiment_pipe, _summary_pipe, _zs_pipe


# --- 2. Topic labels we would like to detect (if zero-shot works) ----------

TOPIC_LABELS = [
    "inflation",
    "interest rates",
    "jobs",
    "labor market",
    "earnings",
    "recession",
    "growth",
    "stocks",
    "bonds",
    "central bank",
]


def annotate_article_text(text: str):
    """
    Given article text (title or raw_text), return:
    - sentiment_label  (e.g. 'POSITIVE', 'NEGATIVE', 'NEUTRAL')
    - sentiment_score  (float, confidence)
    - summary          (short abstractive summary)
    - topics_str       (comma-separated topics or '' if not available)
    """
    sentiment_pipe, summary_pipe, zs_pipe = get_pipelines()

    # 1) Sentiment — we truncate text to keep it cheap
    s_res = sentiment_pipe(text[:512])[0]
    sentiment_label = s_res["label"]
    sentiment_score = float(s_res["score"])

    # 2) Summary — works even for short text, but best with a bit more content
    sum_res = summary_pipe(
        text,
        max_length=60,
        min_length=15,
        do_sample=False,
    )[0]["summary_text"]

    # 3) Topics — only if zero-shot pipeline loaded successfully
    if zs_pipe is not None:
        zs_res = zs_pipe(text, TOPIC_LABELS, multi_label=True)
        labels = zs_res["labels"]
        scores = zs_res["scores"]
        # Keep topics with reasonably high score (e.g. >= 0.3)
        tagged = [lab for lab, score in zip(labels, scores) if score >= 0.3]
        topics_str = ", ".join(tagged)
    else:
        topics_str = ""

    return sentiment_label, sentiment_score, sum_res, topics_str


# --- 3. Main entry point: run NLP on NewsArticle rows ----------------------


def run_news_nlp(limit: int = 50):
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

    if not qs:
        print("No articles need NLP right now.")
        return

    print(f"Running NLP on {qs.count()} articles...")

    for art in qs:
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