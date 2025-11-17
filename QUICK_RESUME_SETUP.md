# Quick Setup: Resume-Ready Deployment

## 🎯 Goal: Get Your Dashboard Live and Auto-Updating

## Option 1: Railway.app (Recommended - Easiest)

### Step 1: Push to GitHub
```bash
git init
git add .
git commit -m "MarketPulse - Financial Market Analysis Platform"
git remote add origin https://github.com/yourusername/marketpulse.git
git push -u origin main
```

### Step 2: Deploy on Railway
1. Go to https://railway.app
2. Sign up with GitHub
3. "New Project" → "Deploy from GitHub repo"
4. Select your repo
5. Railway auto-detects Docker

### Step 3: Add Database
- Click "+ New" → "Database" → "PostgreSQL"
- Railway sets `DATABASE_URL` automatically

### Step 4: Set Environment Variables
In Railway dashboard → Variables:
```
FRED_API_KEY=43e833b6295bbba47d543d7a70ff7b5c
NEWSAPI_KEY=your-newsapi-key (optional)
DJANGO_SECRET_KEY=generate-new-one
DEBUG=False
ALLOWED_HOSTS=*.railway.app
```

### Step 5: Set Up Auto-Updates
- Railway Dashboard → Your Service → "Cron Jobs"
- Add: `0 6 * * *` (daily at 6 AM UTC)
- Command: `python manage.py update_marketpulse`

### Step 6: Get Your URL
- Railway provides: `https://your-app.railway.app`
- Dashboard: `https://your-app.railway.app/dashboard/`

**Done!** Your dashboard now updates daily automatically.

---

## Option 2: Docker with Auto-Updates (Local/Server)

If you're running Docker locally or on a server:

### Your docker-compose.yml Now Includes:
- ✅ `scheduler` service that runs daily updates
- ✅ Automatic restarts if containers crash
- ✅ Logs all updates

### To Start:
```bash
docker-compose up -d
```

### Verify Updates Are Running:
```bash
# Check scheduler logs
docker-compose logs scheduler

# Check last update
docker-compose exec web python manage.py shell -c "
from core.models import FeatureFrame
print('Last data:', FeatureFrame.objects.order_by('-date').first().date)"
```

**Updates run daily at 6 AM UTC automatically!**

---

## 📋 What Gets Updated Daily

1. ✅ Economic data (FRED)
2. ✅ Market data (Yahoo Finance)
3. ✅ News articles (NewsAPI)
4. ✅ ML model retraining
5. ✅ Feature frames
6. ✅ NLP processing

---

## 🔍 Verify It's Working

### Check Dashboard:
- Visit your URL
- Check news dates (should be recent)
- Check chart data (should show today/yesterday)
- Check macro snapshot date

### Check Logs:
```bash
# Docker
docker-compose logs scheduler

# Or view update log file
tail -f logs/cron.log
```

---

## 🎯 For Your Resume

**Link Format:**
```
Live Demo: https://your-app.railway.app/dashboard/
```

**What to Say:**
> "MarketPulse - Full-stack financial market analysis platform
> - Real-time dashboard with ML predictions
> - Automated ETL pipelines from multiple data sources
> - NLP-powered news sentiment analysis
> - Live demo: [your-link]
> - Data updates daily at 6 AM EST"

---

## ⚠️ Important Notes

1. **Free Tiers:**
   - Railway: 500 hours/month (enough for always-on)
   - Render: Sleeps after inactivity (upgrade for always-on)

2. **API Limits:**
   - FRED: Very generous free tier
   - NewsAPI: 100 requests/day (free tier)
   - yfinance: No limits

3. **Monitoring:**
   - Set up UptimeRobot (free) to monitor if site goes down
   - Check weekly that updates are running

---

## 🆘 Quick Troubleshooting

**Data looks old?**
```bash
# Manual update
docker-compose exec web python manage.py update_marketpulse
```

**Site not loading?**
- Check containers: `docker-compose ps`
- Check logs: `docker-compose logs web`
- Verify environment variables

**Updates not running?**
- Check scheduler: `docker-compose logs scheduler`
- Verify cron is set: `docker-compose exec scheduler crontab -l`

---

## ✅ You're All Set!

Your dashboard will now:
- ✅ Update automatically every day
- ✅ Stay accessible 24/7
- ✅ Look professional
- ✅ Be ready for your resume!

**Time to deploy:** ~15 minutes
**Cost:** Free (on free tiers)
**Maintenance:** Check monthly

🚀 **Ready to share!**

