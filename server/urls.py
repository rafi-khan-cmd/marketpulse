"""
URL configuration for server project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from core.views import (
    DashboardView,
    SPXDirectionView,
    TimeSeriesView,
    MacroSnapshotView,
    NewsListView,
)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("api/spx-direction/", SPXDirectionView.as_view(), name="spx-direction"),
    path("api/timeseries/", TimeSeriesView.as_view(), name="timeseries"),
    path("api/macro-snapshot/", MacroSnapshotView.as_view(), name="macro-snapshot"),
    path("api/news/", NewsListView.as_view(), name="news-list"),
]