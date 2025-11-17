# MarketPulse Setup Guide

## Required API Keys

This project requires API keys for certain data sources:

### 1. FRED API Key (Required for Economic Data)
- **What it's for**: Fetches economic indicators (CPI, unemployment, interest rates, etc.)
- **How to get it**: 
  1. Go to https://fred.stlouisfed.org/docs/api/api_key.html
  2. Sign up for a free account
  3. Get your API key
- **How to set it**:
  ```bash
  export FRED_API_KEY="your_api_key_here"
  ```
  Or add it to your shell profile (`~/.zshrc` or `~/.bashrc`):
  ```bash
  echo 'export FRED_API_KEY="your_api_key_here"' >> ~/.zshrc
  source ~/.zshrc
  ```

### 2. NewsAPI Key (Optional - for News ETL)
- **What it's for**: Fetches business news headlines
- **How to get it**: 
  1. Go to https://newsapi.org/register
  2. Sign up for a free account (free tier: 100 requests/day)
  3. Get your API key
- **How to set it**:
  ```bash
  export NEWSAPI_KEY="your_api_key_here"
  ```
  Or add it to your shell profile:
  ```bash
  echo 'export NEWSAPI_KEY="your_api_key_here"' >> ~/.zshrc
  source ~/.zshrc
  ```

## Quick Start

1. **Activate virtual environment**:
   ```bash
   source venv/bin/activate
   ```

2. **Set API keys** (see above)

3. **Run the update pipeline**:
   ```bash
   python manage.py update_marketpulse
   ```

4. **Start the development server**:
   ```bash
   python manage.py runserver
   ```

5. **View the dashboard**:
   Open http://127.0.0.1:8000/dashboard/ in your browser

## Notes

- **FRED API Key is required** for economic data (CPI, unemployment, interest rates)
- **NewsAPI Key is optional** - the pipeline will still run but won't fetch news without it
- Market data (SPY, VIX) is fetched from yfinance and doesn't require an API key
- The first run may take a while as it downloads ML models from Hugging Face

