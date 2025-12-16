from django.db import models

# Create your models here.

class Series(models.Model):
    code = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=256, unique=True)
    freq = models.CharField(max_length=8, default="D")
    source = models.CharField(max_length=32, default="FRED")

    def __str__(self):
        return self.code


class Observation(models.Model):
    series = models.ForeignKey(
        Series,
        on_delete=models.CASCADE,
        related_name="obv",
    )
    date = models.DateField(db_index=True)
    value = models.FloatField()

    class Meta:
        unique_together = ("series", "date")
        indexes = [models.Index(fields=["series", "date"])]


class NewsArticle(models.Model):
    """
    Single news article / headline.
    We keep both raw data (tickers, raw_text) and NLP outputs
    (summary, sentiment, topics) on this model.
    """
    # Raw article info
    source = models.CharField(max_length=100)              # e.g. 'Reuters', 'CNBC'
    title = models.CharField(max_length=500)
    url = models.URLField(max_length=500)
    published_at = models.DateTimeField(db_index=True)

    # Optional metadata
    tickers = models.JSONField(default=list, blank=True)   # e.g. ["AAPL", "MSFT"]
    raw_text = models.TextField(blank=True)                # full article text if you ever scrape it

    # NLP fields (we'll fill these later with Hugging Face)
    summary = models.TextField(blank=True)
    sentiment_label = models.CharField(                   # 'positive', 'neutral', 'negative', etc.
        max_length=20,
        blank=True
    )
    sentiment_score = models.FloatField(                  # probability/confidence
        null=True,
        blank=True
    )
    topics = models.TextField(                            # JSON string or comma-separated tags
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-published_at"]

    def __str__(self):
        return f"[{self.source}] {self.title[:80]}"


class FeatureFrame(models.Model):
    date = models.DateField(db_index=True, unique=True)
    features = models.JSONField(default=dict)
    target = models.FloatField(null=True, blank=True)
    label = models.IntegerField(null=True, blank=True)


class ModelArtifact(models.Model):
    name = models.CharField(max_length=64)
    data = models.BinaryField()  # Store serialized model as binary blob
    created_at = models.DateTimeField(auto_now_add=True)
    metrics = models.JSONField(default=dict)


class Prediction(models.Model):
    model = models.ForeignKey(ModelArtifact, on_delete=models.CASCADE)
    date = models.DateField(db_index=True)
    yhat = models.FloatField()
    details = models.JSONField(default=dict)

    class Meta:
        unique_together = ("model", "date")