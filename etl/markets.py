import datetime as dt
from typing import Dict, Tuple
import pandas as pd
import yfinance as yf
from core.models import Series, Observation

# Map of tickers to fetch. SPY is used for both SPX_CLOSE (close price) and SPY_VOLUME
YF_TICKERS = {
    "SPY": "SPY",   # Use SPY ETF as proxy for S&P 500 (tracks S&P 500 closely)
    "^VIX": "^VIX", # VIX volatility index
}

def fetch_yf_history(ticker:str, period: str = "max"):
    """Fetch yfinance data with retry and error handling."""
    try:
        ticker_obj = yf.Ticker(ticker)
        df = ticker_obj.history(period=period)
        return df
    except Exception as e:
        print(f"Error fetching {ticker}: {e}")
        # Try alternative ticker symbols
        alternatives = {
            "^GSPC": "SPY",  # Use SPY ETF as proxy for S&P 500
            "^VIX": "VIX",   # Keep VIX as is
        }
        if ticker in alternatives:
            alt_ticker = alternatives[ticker]
            print(f"Trying alternative ticker: {alt_ticker}")
            try:
                ticker_obj = yf.Ticker(alt_ticker)
                df = ticker_obj.history(period=period)
                return df
            except Exception as e2:
                print(f"Alternative ticker {alt_ticker} also failed: {e2}")
        return pd.DataFrame()  # Return empty DataFrame on failure

def run_markets_etl(period:str = "max"):
    # Fetch SPY data (used for both SPX_CLOSE and SPY_VOLUME)
    print("Fetching SPY -> SPX_CLOSE and SPY_VOLUME ...")
    spy_df = fetch_yf_history("SPY", period=period)
    
    if not spy_df.empty:
        spy_df = spy_df.sort_index()
        
        # Store SPX_CLOSE (using SPY close price as proxy)
        spx_series, _ = Series.objects.get_or_create(
            code="SPX_CLOSE",
            defaults={"name": "S&P 500 Close", "freq": "D", "source": "YF"},
        )
        spx_count = 0
        for date_index, row in spy_df.iterrows():
            value = float(row['Close'])
            as_date = date_index.date()
            Observation.objects.update_or_create(
                series=spx_series,
                date=as_date,
                defaults={"value": value},
            )
            spx_count += 1
        print(f" -> stored {spx_count} rows for SPX_CLOSE")
        
        # Store SPY_VOLUME
        vol_series, _ = Series.objects.get_or_create(
            code="SPY_VOLUME",
            defaults={"name": "SPY Volume", "freq": "D", "source": "YF"},
        )
        vol_count = 0
        for date_index, row in spy_df.iterrows():
            value = float(row['Volume'])
            as_date = date_index.date()
            Observation.objects.update_or_create(
                series=vol_series,
                date=as_date,
                defaults={"value": value},
            )
            vol_count += 1
        print(f" -> stored {vol_count} rows for SPY_VOLUME")
    else:
        print("No SPY data returned")
    
    # Fetch VIX data
    print("Fetching ^VIX -> VIX ...")
    vix_df = fetch_yf_history("^VIX", period=period)
    
    if not vix_df.empty:
        vix_df = vix_df.sort_index()
        vix_series, _ = Series.objects.get_or_create(
            code="VIX",
            defaults={"name": "VIX Index", "freq": "D", "source": "YF"},
        )
        vix_count = 0
        for date_index, row in vix_df.iterrows():
            value = float(row['Close'])
            as_date = date_index.date()
            Observation.objects.update_or_create(
                series=vix_series,
                date=as_date,
                defaults={"value": value},
            )
            vix_count += 1
        print(f" -> stored {vix_count} rows for VIX")
    else:
        print("No VIX data returned")

