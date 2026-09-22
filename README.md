# MarketPulse

A financial-market analysis platform that pulls together macroeconomic data, market indicators, and business news, runs NLP over the headlines, and trains a model to predict the next-day direction of the S&P 500. Everything is wired into a Django app with an interactive dashboard.

**Live demo:** https://marketpulse-production-a407.up.railway.app/dashboard/

## What it does

**ETL** — Scheduled pipelines fetch economic indicators from the FRED API (CPI, unemployment, interest rates, term spread), market data from Yahoo Finance (S&P 500, VIX, volume), and business headlines from NewsAPI.

**Feature engineering** — Raw series are combined into feature frames, including composite indicators like a Macro Heat Index and a Risk Barometer.

**Machine learning** — A logistic-regression model predicts whether the S&P 500 will close up or down the next day, with an automated retraining step. Current test accuracy is around 62% (a coin flip is 50%).

**NLP** — News articles are run through Hugging Face transformers for sentiment classification, abstractive summarization, and zero-shot topic tagging (inflation, interest rates, earnings, and so on).

**Dashboard** — A single-page dashboard (Chart.js + Tailwind) shows market trends, the macro snapshot, the news feed with sentiment/topics, and the latest direction prediction with its probability.

## Stack

- **Backend:** Django 5.1, Django REST Framework, SQLite (swappable for Postgres)
- **Data/ML:** pandas, numpy, scikit-learn, joblib
- **NLP:** Hugging Face transformers on PyTorch
- **Data sources:** yfinance, FRED API, NewsAPI
- **Frontend:** Chart.js, Tailwind CSS
- **Deploy:** Docker / docker-compose, Railway (`railway.json`), Render (`render.yaml`)

## Quick start

You'll need a free [FRED API key](https://fred.stlouisfed.org/docs/api/api_key.html) and optionally a [NewsAPI key](https://newsapi.org/).

```bash
git clone https://github.com/rafi-khan-cmd/marketpulse.git
cd marketpulse

python3 -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt

export FRED_API_KEY="your_fred_api_key"
export NEWSAPI_KEY="your_newsapi_key"        # optional
export DJANGO_SECRET_KEY="your_secret_key"   # generate a fresh one for production

python manage.py migrate
python manage.py update_marketpulse          # fetches data, builds features, trains, pulls news
python manage.py runserver
```

Then open http://127.0.0.1:8000/dashboard/.

## Project structure

```
marketpulse/
├── api/              # REST API endpoints
├── core/             # models, dashboard views, management commands
│   ├── models.py     # Series, Observation, NewsArticle, FeatureFrame, ModelArtifact
│   └── management/   # update_marketpulse, fetch_news
├── etl/              # ETL: fred.py, markets.py, news_api.py, features.py
├── ml/               # train_spx_model.py, predict_spx.py, news_nlp.py
├── server/           # Django settings
├── Dockerfile, docker-compose.yml, railway.json, render.yaml
└── requirements.txt
```

The trained model is serialized and stored in the database as a `ModelArtifact` row, so there's no separate model file to track.

## Management commands

```bash
python manage.py update_marketpulse   # full pipeline: ETL, features, training, news
python manage.py fetch_news           # news + NLP refresh only
```

To keep the live dashboard current, `setup_scheduled_updates.sh` and `AUTO_UPDATE_SETUP.md` show how to run `update_marketpulse` on a daily schedule (cron or a hosted cron service).

## API

- `GET /api/timeseries/?code=SPX_CLOSE` — time series for a series code
- `GET /api/macro-snapshot/` — latest macro snapshot
- `GET /api/news/?limit=20` — latest news with sentiment/topics
- `GET /api/spx-direction/` — latest SPX direction prediction

## Tests

```bash
python manage.py test                 # or: test core.tests / etl.tests / ml.tests
```

Tests cover the models, API endpoints, feature engineering, ETL, and prediction logic.

## Notes on the model

The direction model is deliberately simple — logistic regression over market and macro features. Predicting daily index direction is genuinely hard, so ~62% is a modest but honest edge over the 50% baseline. The point of the project was the end-to-end pipeline (ingest → features → train → serve → visualize), not squeezing out maximum accuracy.

## Author

Rafiul Alam Khan
[GitHub](https://github.com/rafi-khan-cmd) · [LinkedIn](https://www.linkedin.com/in/rafiul-alam-k-3a20392b0/) · alamkhanrafiul@gmail.com
