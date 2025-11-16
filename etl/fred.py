import os 
from datetime import datetime
from typing import List, Tuple, Dict

import requests

from core.models import Series, Observation

FRED_API_KEY = os.getenv("FRED_API_KEY")
FRED_API_URL = "https://api.stlouisfed.org/fred/series/observations"

FRED_SERIES_MAP: Dict[str, str] = {          # 8
    "CPIAUCSL": "CPI",                       # 9
    "CPILFESL": "CoreCPI",                   # 10
    "PCEPI":    "PCE",                       # 11
    "PCEPILFE": "CorePCE",                   # 12
    "UNRATE":   "Unemployment",              # 13
    "ICSA":     "JoblessClaims",             # 14
    "FEDFUNDS": "FFR",                       # 15
    "DGS10":    "US10Y",                     # 16
    "DGS2":     "US2Y",                      # 17
}


def fetch_fred_series(series_id: str) -> List[Tuple[datetime.date, float]]:
    if not FRED_API_KEY:
        raise RuntimeError("FRED_API_KEY is not set in environment")

    params = {
        "series_id" : series_id,
        "api_key" : FRED_API_KEY,
        "file_type": "json",
    }

    resp = requests.get(FRED_API_URL, params = params)
    resp.raise_for_status()
    payload = resp.json()
    observations = payload["observations"]

    rows: List[Tuple[datetime.date, float]] = []
    for obs in observations:
        if obs["value"] == ".":
            continue
        dt = datetime.fromisoformat(obs["date"]).date()
        val = float(obs["value"])
        rows.append((dt,val))

    return rows

def run_fred_etl() -> None:
    for fred_id, code in FRED_SERIES_MAP.items():
        print(f"Fetching {fred_id} -> {code} ...")
        rows = fetch_fred_series(fred_id)
        series, _ = Series.objects.get_or_create(
            code = code,
            defaults = {
                "name": code,
                "freq": "M",
                "source" : "FRED", 
            },
        )

        count = 0
        for dt, val in rows:
            Observation.objects.update_or_create(
                series = series,
                date = dt,
                defaults ={"value": val},
            )
            count = count + 1
        print(f" -> stored {count} rows for {code}")