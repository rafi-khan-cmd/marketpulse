# 🚀 Publish MarketPulse - Quick Steps

## Fastest Way: Railway.app (Recommended)

### ⏱️ Total Time: ~20 minutes

---

## Step 1: Push to GitHub (5 min)

```bash
cd /Users/rafiulalamkhan/MarketPulseCursor/marketpulse

# Initialize git (if needed)
git init

# Add all files
git add .

# Commit
git commit -m "MarketPulse - Financial Market Analysis Platform"

# Create repo on GitHub.com, then:
git remote add origin https://github.com/YOUR_USERNAME/marketpulse.git
git branch -M main
git push -u origin main
```

---

## Step 2: Deploy on Railway (10 min)

1. **Go to:** https://railway.app
2. **Sign up** with GitHub
3. **"New Project"** → **"Deploy from GitHub repo"**
4. **Select** your `marketpulse` repo
5. **Railway auto-detects** Docker - wait for build

---

## Step 3: Add Database (2 min)

1. Click **"+ New"** button
2. Select **"Database"** → **"Add PostgreSQL"**
3. Railway automatically connects it

---

## Step 4: Set Environment Variables (3 min)

Go to your service → **"Variables"** tab → Add:

```
FRED_API_KEY=43e833b6295bbba47d543d7a70ff7b5c
NEWSAPI_KEY=your-newsapi-key (optional)
DJANGO_SECRET_KEY=generate-new-secret-key
DEBUG=False
ALLOWED_HOSTS=*.railway.app
```

**Generate SECRET_KEY:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## Step 5: Set Up Auto-Updates (2 min)

1. Railway Dashboard → Your Project
2. Click **"Cron Jobs"** or **"Scheduled Tasks"**
3. Add:
   - **Schedule**: `0 6 * * *` (daily at 6 AM UTC)
   - **Command**: `python manage.py update_marketpulse`

---

## Step 6: Load Initial Data (5 min)

1. Railway Dashboard → Your Service → **"Logs"**
2. Click **"Open Terminal"** (or use Railway CLI)
3. Run:
   ```bash
   python manage.py update_marketpulse
   ```
4. Wait for it to complete (5-10 min first time)

---

## Step 7: Get Your URL

Railway provides: `https://your-app-name.railway.app`

**Your dashboard:** `https://your-app-name.railway.app/dashboard/`

**Copy this URL for your resume!** ✅

---

## ✅ Verify It Works

1. Visit your dashboard URL
2. Check all charts load
3. Check news feed works
4. Check predictions show
5. Test on mobile device

---

## 📝 For Your Resume

**Link:**
```
Live Demo: https://your-app-name.railway.app/dashboard/
```

**Description:**
> MarketPulse - Financial Market Analysis Platform
> 
> Full-stack Django application with real-time market analysis, 
> ML predictions, and NLP-powered news sentiment analysis.
> 
> Live Demo: [your-link]
> 
> Technologies: Python, Django, PostgreSQL, Docker, Machine Learning, NLP

---

## 🔄 Keeping It Updated

✅ **Already set up!** The cron job updates data daily at 6 AM UTC automatically.

**Check updates:**
- Railway Dashboard → Logs
- Should see daily update logs

---

## 🆘 Troubleshooting

**Site not loading?**
- Check Railway logs
- Verify environment variables
- Check `ALLOWED_HOSTS`

**Data not updating?**
- Check cron job is scheduled
- View cron logs
- Test manual update

**Need help?**
- Railway Docs: https://docs.railway.app
- Railway Discord: https://discord.gg/railway

---

## 🎉 Done!

Your dashboard is now:
- ✅ Live and accessible 24/7
- ✅ Updating automatically daily
- ✅ Ready to share on your resume!

**Share the link with confidence!** 🚀

