# MarketPulse Data Ranges

## 📊 Current Data Coverage

### Market Data (Yahoo Finance)
- **SPX/SPY**: Now fetches **MAXIMUM available** (SPY since 1993 = ~30+ years)
- **VIX**: Now fetches **MAXIMUM available** (~30+ years)
- **Volume**: Now fetches **MAXIMUM available** (~30+ years)

**Previously:** Only 5 years (2020-2025)  
**Now:** All available historical data (~30+ years)

### Economic Data (FRED API)
- **CPI**: 1947-2025 (~78 years) ✅
- **Core CPI**: 1957-2025 (~68 years) ✅
- **Unemployment**: 1948-2025 (~77 years) ✅
- **Jobless Claims**: 1967-2025 (~58 years) ✅
- **Fed Funds Rate**: 1954-2025 (~71 years) ✅
- **10Y Treasury**: 1962-2025 (~64 years) ✅
- **2Y Treasury**: 1976-2025 (~49 years) ✅

**Status:** Already fetching all available data ✅

### ML Model Training Data
- **Now:** ~30+ years of data (limited by SPX availability)
- **Features:** Uses all available economic indicators (some going back to 1947)
- **Training:** Model trains on all available FeatureFrame rows

## 🔄 What Changed

**Updated:** `etl/markets.py`
- Changed default period from `"5y"` to `"max"`
- Now fetches all available historical market data
- ML model will train on ~30+ years instead of 5 years

## 📈 Impact on Model

**Before:**
- Training data: ~1,825 days (5 years)
- Limited historical context
- Less robust to different market conditions

**After:**
- Training data: ~7,500+ days (30+ years)
- Includes multiple market cycles (bull, bear, recession, recovery)
- More robust predictions
- Better generalization

## 🔍 To See the Full Data Range

After running `update_marketpulse` with the new settings:

```bash
python manage.py shell -c "
from core.models import Series, Observation
spx = Series.objects.get(code='SPX_CLOSE')
obs = Observation.objects.filter(series=spx).order_by('date')
print(f'SPX data: {obs.first().date} to {obs.last().date}')
print(f'Total days: {obs.count()}')
print(f'Years: {(obs.last().date - obs.first().date).days / 365.25:.1f}')
"
```

## ⚙️ Customizing Data Range

If you want to limit to a specific period, you can:

```python
# In update_marketpulse command or directly:
from etl.markets import run_markets_etl

# Fetch last 10 years
run_markets_etl(period="10y")

# Fetch last 20 years  
run_markets_etl(period="20y")

# Fetch maximum (default now)
run_markets_etl(period="max")
```

## 📝 Notes

- **First run with "max"** will take longer (fetching ~30 years of data)
- **Subsequent runs** are incremental (only new data)
- **Database size** will increase but still manageable
- **Model training** will take slightly longer but produce better results

## ✅ Benefits of Maximum Data

1. **Better ML Model:**
   - More training examples
   - Exposure to different market regimes
   - Better generalization

2. **More Comprehensive Analysis:**
   - Historical context in charts
   - Long-term trends visible
   - Better for portfolio demonstration

3. **More Impressive for Resume:**
   - Shows handling of large datasets
   - Demonstrates scalability
   - Professional data management

---

**Current Status:** ✅ Now fetching maximum available data for all sources!

