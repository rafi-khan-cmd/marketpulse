# MarketPulse 📈

A comprehensive financial market analysis platform that combines macroeconomic data, market indicators, news sentiment analysis, and machine learning predictions to provide real-time insights into market trends.

## 🎯 Project Overview

MarketPulse is a full-stack Django application that aggregates data from multiple sources (FRED, Yahoo Finance, NewsAPI) and uses machine learning and NLP to analyze and predict market movements. The platform features an interactive dashboard with real-time visualizations of economic indicators, market trends, and news sentiment.

## ✨ Key Features

### Data Integration & ETL
- **Economic Data**: Automated ETL pipeline fetching indicators from FRED API (CPI, unemployment, interest rates, etc.)
- **Market Data**: Real-time market data from Yahoo Finance (S&P 500, VIX, trading volume)
- **News Aggregation**: Business news headlines from NewsAPI with automated processing

### Machine Learning
- **SPX Direction Prediction**: Logistic regression model predicting next-day S&P 500 direction
- **Feature Engineering**: Composite indicators including Macro Heat Index and Risk Barometer
- **Model Training**: Automated retraining pipeline with performance metrics

### Natural Language Processing
- **Sentiment Analysis**: Real-time sentiment classification of news articles using Hugging Face transformers
- **Text Summarization**: Automatic abstractive summarization of news headlines
- **Topic Extraction**: Zero-shot classification to identify relevant topics (inflation, interest rates, earnings, etc.)

### Interactive Dashboard
- **Real-time Visualizations**: Multiple Chart.js charts showing market trends, economic indicators, and yield curves
- **Macro Snapshot**: Composite metrics including Macro Heat Index and Risk Barometer
- **News Feed**: Latest business news with sentiment scores and topic tags
- **ML Predictions**: Real-time SPX direction predictions with probability scores

### RESTful API
- Time series data endpoints
- Macro snapshot API
- News listing API
- SPX direction prediction API

## 🛠️ Tech Stack

### Backend
- **Django 5.1.6**: Web framework
- **Django REST Framework**: API development
- **SQLite**: Database (easily configurable for PostgreSQL/MySQL)

### Data Science & ML
- **pandas**: Data manipulation and analysis
- **numpy**: Numerical computing
- **scikit-learn**: Machine learning (logistic regression)
- **joblib**: Model serialization

### NLP
- **transformers (Hugging Face)**: Pre-trained models for sentiment analysis and summarization
- **PyTorch**: Deep learning backend

### Data Sources
- **yfinance**: Market data (S&P 500, VIX, volume)
- **FRED API**: Economic indicators
- **NewsAPI**: Business news headlines

### Frontend
- **Chart.js**: Interactive data visualizations
- **Tailwind CSS**: Modern, responsive UI

## 📋 Prerequisites

- Python 3.11+
- pip
- FRED API key (free at https://fred.stlouisfed.org/docs/api/api_key.html)
- NewsAPI key (optional, free tier available at https://newsapi.org/)

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone <repository-url>
cd marketpulse
```

### 2. Set Up Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Environment Variables
```bash
export FRED_API_KEY="your_fred_api_key"
export NEWSAPI_KEY="your_newsapi_key"  # Optional
export DJANGO_SECRET_KEY="your_secret_key"  # Generate a new one for production
```

### 5. Run Migrations
```bash
python manage.py migrate
```

### 6. Fetch Data and Train Model
```bash
python manage.py update_marketpulse
```

This command will:
- Fetch economic data from FRED
- Fetch market data from Yahoo Finance
- Build feature frames
- Train the ML model
- Fetch and process news articles

### 7. Start Development Server
```bash
python manage.py runserver
```

### 8. Access Dashboard
Open http://127.0.0.1:8000/dashboard/ in your browser

## 📁 Project Structure

```
marketpulse/
├── api/              # API endpoints
├── core/             # Core models and views
│   ├── models.py     # Database models (Series, Observation, NewsArticle, FeatureFrame)
│   ├── views.py      # Dashboard and API views
│   └── management/   # Django management commands
├── etl/              # ETL pipelines
│   ├── fred.py       # FRED API integration
│   ├── markets.py    # Yahoo Finance integration
│   ├── news_api.py   # NewsAPI integration
│   └── features.py   # Feature engineering
├── ml/               # Machine learning
│   ├── train_spx_model.py  # Model training
│   ├── predict_spx.py      # Prediction logic
│   └── news_nlp.py         # NLP processing
├── server/           # Django settings and configuration
├── models/           # Trained ML model artifacts
└── requirements.txt  # Python dependencies
```

## 🔧 Management Commands

### Update All Data
```bash
python manage.py update_marketpulse
```
Runs the complete ETL pipeline, feature engineering, model training, and news processing.

### Fetch News Only
```bash
python manage.py fetch_news
```
Fetches latest news and runs NLP processing.

## 📊 API Endpoints

- `GET /api/timeseries/?code=SPX_CLOSE` - Get time series data for a series code
- `GET /api/macro-snapshot/` - Get latest macroeconomic snapshot
- `GET /api/news/?limit=20` - Get latest news articles with NLP data
- `GET /api/spx-direction/` - Get latest SPX direction prediction
- `GET /dashboard/` - Interactive dashboard

## 🧪 Testing

The project includes comprehensive unit tests for models, views, ETL functions, and ML components.

Run all tests:
```bash
python manage.py test
```

Run specific test suites:
```bash
python manage.py test core.tests
python manage.py test etl.tests
python manage.py test ml.tests
```

Test coverage includes:
- Model creation and validation
- API endpoint functionality
- Feature engineering functions
- ETL pipeline components
- ML prediction logic

## 🔒 Security

- **SECRET_KEY** is now loaded from environment variables (not hardcoded)
- All API keys use environment variables
- Production-ready security settings
- See [DEPLOYMENT.md](DEPLOYMENT.md) for production security checklist

## 📈 Model Performance

The SPX direction prediction model uses logistic regression with the following features:
- Market indicators (SPX close, returns, VIX, volume)
- Economic indicators (CPI, unemployment, interest rates, term spread)

Current test accuracy: ~62% (baseline for binary classification: 50%)

## 🚢 Deployment

The project includes Docker support and comprehensive deployment documentation.

### Quick Docker Deployment
```bash
docker-compose up -d
```

### Options Available
- **Docker & Docker Compose**: Included with `Dockerfile` and `docker-compose.yml`
- **Gunicorn + Nginx**: Traditional server deployment
- **Cloud Platforms**: Heroku, Railway, AWS Elastic Beanstalk

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions for all platforms.

## 📝 License

This project is open source and available for educational purposes.

## 👤 Author

Built as a portfolio project demonstrating:
- Full-stack web development (Django, REST APIs)
- Data engineering (ETL pipelines, feature engineering)
- Machine learning (model training, prediction)
- NLP (sentiment analysis, text summarization)
- Data visualization (interactive dashboards)

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

## 📚 Additional Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [FRED API Documentation](https://fred.stlouisfed.org/docs/api/)
- [Hugging Face Transformers](https://huggingface.co/docs/transformers)

