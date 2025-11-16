import datetime as dt
from typing import Dict, Tuple
import yfinance as yf
from core.models import Series, Observation

YF_SERIES_MAP: Dict[str, Tuple[str, str]] = {     # 5
    "^GSPC": ("SPX_CLOSE", "S&P 500 Close"),      # 6
    "^VIX":  ("VIX",       "VIX Index"),          # 7
    "SPY":   ("SPY_VOLUME","SPY Volume"),         # 8
}

def fetch_yf_history(ticker:str, period: str = "5y"):
    return yf.Ticker(ticker).history(period=period)

def run_markets_etl(period:str = "5y"):
    for ticker, (code, name) in YF_SERIES_MAP.items():
        print(f"Fetching {ticker} -> {code} ...")
        df = fetch_yf_history(ticker, period = period)

        if df.empty:
            print(f"No data returned for {ticker}")

        df = df.sort_index()

        series, _ = Series.objects.get_or_create(
            code = code,
            defaults = {
                "name": name,
                "freq": "D",
                "source": "YF",
            },
        )

        count = 0

        if code == "SPX_CLOSE":
            for date_index, row in df.iterrows():
                value = float(row['Close'])
                as_date = date_index.date()
                Observation.objects.update_or_create(
                    series = series,
                    date = as_date,
                    defaults = {"value": value},
                )
                count = count + 1

        elif code == "VIX":
            for date_index, row in df.iterrows():
                value = float(row['Close'])
                as_date = date_index.date()
                Observation.objects.update_or_create(
                    series = series,
                    date = as_date,
                    defaults = {"value": value}
                )
                count = count + 1

        elif code == "SPY_VOLUME":
            for date_index, row in df.iterrows():
                value = float(row['Volume'])
                as_date = date_index.date()
                Observation.objects.update_or_create(
                    series = series,
                    date = as_date,
                    defaults = {"value": value},
                )

                count = count + 1
        
        print(f" -> stored {count} rows for {code}")

