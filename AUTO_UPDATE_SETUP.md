# 🔄 Automatic Daily Updates Setup

Your MarketPulse dashboard needs to update daily to stay fresh for resume reviewers.

## Quick Setup (5 minutes)

### Step 1: Use cron-job.org (Free)

1. Go to https://cron-job.org
2. Sign up (free account)
3. Click **"Create cronjob"**
4. Fill in:
   - **Title:** MarketPulse Daily Update
   - **Address:** `https://marketpulse-production-a407.up.railway.app/api/update/`
   - **Schedule:** Daily at 6:00 AM (or your preferred time)
   - **Timezone:** Your timezone
5. Click **"Create"**

✅ **Done!** Your data will update automatically every day.

---

## What Gets Updated Daily

- ✅ Latest market data (SPX, VIX, Volume)
- ✅ Economic indicators (CPI, unemployment, rates)
- ✅ News articles with sentiment analysis
- ✅ ML model retraining
- ✅ All charts and predictions

---

## Verify It's Working

1. After setting up, wait until the scheduled time
2. Check your dashboard - data should be fresh
3. Or test manually: Visit `https://marketpulse-production-a407.up.railway.app/api/update/`

---

## Alternative Services

- **EasyCron:** https://www.easycron.com (free tier)
- **UptimeRobot:** https://uptimerobot.com (monitors + can trigger updates)

---

## Your Update Endpoint

```
https://marketpulse-production-a407.up.railway.app/api/update/
```

This endpoint triggers the full data update pipeline. The cron service will call it daily.

---

## Best Time to Schedule

**Recommended: 6:00 AM UTC** (or 1-2 AM EST)
- Markets are closed
- Fresh data available
- Won't interfere with traffic

---

## Troubleshooting

**Updates not running?**
- Check cron-job.org dashboard for execution logs
- Verify the URL is correct
- Test manually by visiting the endpoint

**Data not updating?**
- Check Railway logs for errors
- Verify API keys are set correctly
- Check Railway service is running

