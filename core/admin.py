from django.contrib import admin

# Register your models here.

from .models import (
    Series,
    Observation,
    NewsArticle,
    FeatureFrame,
    ModelArtifact,
    Prediction,
)

@admin.register(Series)
class SeriesAdmin(admin.ModelAdmin):
    list_display = ("code","name","freq","source")

@admin.register(Observation)
class ObservationAdmin(admin.ModelAdmin):
    list_display = ("series","date","value")
    list_filter = ("series",)
    date_hierarchy = "date"

@admin.register(NewsArticle)
class NewsArticleAdmin(admin.ModelAdmin):
    list_display = ("source","title","published_at")
    search_fields = ("title","url")


@admin.register(FeatureFrame)
class FeatureFrameAdmin(admin.ModelAdmin):
    list_display = ("date",)

@admin.register(ModelArtifact)
class ModelArtifactAdmin(admin.ModelAdmin):
    list_display = ("name","created_at")

@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):
    list_display = ("model", "date","yhat")