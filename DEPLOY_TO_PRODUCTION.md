# Deploy MarketPulse to Production - Step by Step

## 🎯 Goal: Get Your Dashboard Live and Accessible 24/7

This guide will help you deploy MarketPulse to a cloud platform so it stays accessible when employers review your resume.

---

## 🚀 Option 1: Railway.app (Recommended - Easiest & Free)

### Why Railway?
- ✅ Free tier (500 hours/month - enough for always-on)
- ✅ Automatic deployments from GitHub
- ✅ Built-in PostgreSQL database
- ✅ Easy cron job setup
- ✅ Custom domain support
- ✅ No credit card required

### Step-by-Step:

#### Step 1: Prepare Your Code

```bash
# Make sure you're in the project directory
cd /Users/rafiulalamkhan/MarketPulseCursor/marketpulse

# Check what we have
ls -la
```

#### Step 2: Create GitHub Repository

```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Create initial commit
git commit -m "MarketPulse - Financial Market Analysis Platform"

# Create a new repository on GitHub.com, then:
git remote add origin https://github.com/YOUR_USERNAME/marketpulse.git
git branch -M main
git push -u origin main
```

**Or use GitHub Desktop/GitHub CLI if you prefer.**

#### Step 3: Deploy on Railway

1. **Go to Railway:**
   - Visit https://railway.app
   - Click "Start a New Project"
   - Sign up with GitHub (recommended)

2. **Deploy from GitHub:**
   - Click "Deploy from GitHub repo"
   - Select your `marketpulse` repository
   - Railway will auto-detect it's a Docker project

3. **Add PostgreSQL Database:**
   - Click "+ New" button
   - Select "Database" → "Add PostgreSQL"
   - Railway automatically sets `DATABASE_URL` environment variable

4. **Set Environment Variables:**
   - Go to your service → "Variables" tab
   - Add these variables:
     ```
     FRED_API_KEY=43e833b6295bbba47d543d7a70ff7b5c
     NEWSAPI_KEY=your-newsapi-key-here (optional, can leave empty)
     DJANGO_SECRET_KEY=generate-a-new-secret-key-here
     DEBUG=False
     ALLOWED_HOSTS=*.railway.app
     ```
   
   **To generate SECRET_KEY:**
   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

5. **Update Port Configuration:**
   - Railway uses `$PORT` environment variable
   - Update your `Dockerfile` or create `railway.json`:
   
   Create `railway.json`:
   ```json
   {
     "$schema": "https://railway.app/railway.schema.json",
     "build": {
       "builder": "DOCKERFILE",
       "dockerfilePath": "Dockerfile"
     },
     "deploy": {
       "startCommand": "gunicorn --bind 0.0.0.0:$PORT --workers 3 server.wsgi:application",
       "restartPolicyType": "ON_FAILURE",
       "restartPolicyMaxRetries": 10
     }
   }
   ```

6. **Set Up Auto-Updates:**
   - Go to Railway Dashboard → Your Project
   - Click "Cron Jobs" (or "Scheduled Tasks")
   - Add new cron job:
     - **Schedule**: `0 6 * * *` (daily at 6 AM UTC)
     - **Command**: `python manage.py update_marketpulse`
     - **Service**: Select your web service

7. **Get Your URL:**
   - Railway provides: `https://your-app-name.railway.app`
   - Your dashboard: `https://your-app-name.railway.app/dashboard/`
   - Copy this URL for your resume!

#### Step 4: Initial Data Load

After first deployment, load initial data:

1. Go to Railway Dashboard → Your Service → "Logs"
2. Click "Open Terminal" or use Railway CLI:
   ```bash
   railway run python manage.py update_marketpulse
   ```

**Done!** Your dashboard is now live and will update daily.

---

## 🚀 Option 2: Render.com (Also Free, Good Alternative)

### Step-by-Step:

1. **Go to Render:**
   - Visit https://render.com
   - Sign up with GitHub

2. **Create New Web Service:**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Settings:
     - **Name**: marketpulse
     - **Environment**: Docker
     - **Region**: Choose closest to you
     - **Branch**: main
     - **Build Command**: (auto-detected)
     - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT --workers 3 server.wsgi:application`

3. **Add PostgreSQL:**
   - Click "New +" → "PostgreSQL"
   - Render auto-sets `DATABASE_URL`

4. **Set Environment Variables:**
   - Same as Railway above

5. **Set Up Cron Job:**
   - Create "Background Worker" service
   - Command: `python manage.py update_marketpulse`
   - Schedule: Daily at 6 AM

6. **Get Your URL:**
   - Render provides: `https://marketpulse.onrender.com`
   - Dashboard: `https://marketpulse.onrender.com/dashboard/`

**Note:** Free tier sleeps after 15 min inactivity. Upgrade to "Starter" ($7/month) for always-on.

---

## 🚀 Option 3: Fly.io (Good for Docker)

### Step-by-Step:

1. **Install Fly CLI:**
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. **Login:**
   ```bash
   fly auth login
   ```

3. **Create App:**
   ```bash
   fly launch
   ```
   - Follow prompts
   - Choose app name
   - Select region

4. **Set Secrets:**
   ```bash
   fly secrets set FRED_API_KEY=43e833b6295bbba47d543d7a70ff7b5c
   fly secrets set NEWSAPI_KEY=your-key
   fly secrets set DJANGO_SECRET_KEY=your-secret-key
   fly secrets set DEBUG=False
   fly secrets set ALLOWED_HOSTS=your-app.fly.dev
   ```

5. **Add PostgreSQL:**
   ```bash
   fly postgres create --name marketpulse-db
   fly postgres attach marketpulse-db
   ```

6. **Deploy:**
   ```bash
   fly deploy
   ```

7. **Set Up Cron:**
   - Use Fly's scheduled tasks or external service

---

## 📋 Pre-Deployment Checklist

Before deploying, make sure:

- [ ] Code is pushed to GitHub
- [ ] All environment variables are ready
- [ ] `DEBUG=False` for production
- [ ] `ALLOWED_HOSTS` includes your domain
- [ ] New `SECRET_KEY` generated
- [ ] Dockerfile is correct
- [ ] Tests pass locally

---

## 🔧 Update Dockerfile for Cloud Platforms

Some platforms need the `PORT` environment variable. Update your `Dockerfile`:

```dockerfile
# Change the CMD to use PORT env var
CMD gunicorn --bind 0.0.0.0:${PORT:-8000} --workers 3 server.wsgi:application
```

Or create `railway.json` / platform-specific config.

---

## ✅ After Deployment

### 1. Load Initial Data

```bash
# Railway
railway run python manage.py update_marketpulse

# Render (via dashboard terminal)
python manage.py update_marketpulse

# Fly.io
fly ssh console
python manage.py update_marketpulse
```

### 2. Test Your Dashboard

Visit: `https://your-app-url/dashboard/`

Check:
- ✅ Dashboard loads
- ✅ Charts display data
- ✅ News feed works
- ✅ Predictions show
- ✅ All API endpoints work

### 3. Verify Auto-Updates

Wait 24 hours, then check:
- News dates are recent
- Chart data is current
- Macro snapshot date is today/yesterday

---

## 🔗 For Your Resume

**Link Format:**
```
Live Demo: https://your-app.railway.app/dashboard/
Portfolio Project: https://marketpulse.onrender.com/dashboard/
```

**What to Include:**
> "MarketPulse - Financial Market Analysis Platform
> 
> Full-stack Django application with real-time market analysis, 
> ML predictions, and NLP-powered news sentiment analysis.
> 
> Live Demo: [your-link]
> 
> Features:
> - Automated ETL pipelines from FRED, Yahoo Finance, NewsAPI
> - Machine learning model for market direction prediction
> - Interactive dashboard with 8+ real-time charts
> - Data updates daily at 6 AM EST"

---

## 🆘 Troubleshooting

### Site Not Loading

1. Check deployment logs in platform dashboard
2. Verify environment variables are set
3. Check `ALLOWED_HOSTS` includes your domain
4. Ensure database is connected

### Data Not Updating

1. Check cron job is scheduled
2. View cron logs
3. Test manual update
4. Verify API keys

### Database Issues

1. Run migrations:
   ```bash
   python manage.py migrate
   ```
2. Check database connection
3. Verify `DATABASE_URL` is set

---

## 💰 Cost Comparison

| Platform | Free Tier | Always-On | Best For |
|----------|-----------|-----------|----------|
| Railway | 500 hrs/month | ✅ Yes | **Best choice** |
| Render | 750 hrs/month | ❌ Sleeps | Good alternative |
| Fly.io | Limited | ✅ Yes | Advanced users |
| Heroku | None | ❌ | Not recommended |

**Recommendation:** Railway.app for easiest setup with always-on free tier.

---

## 🎯 Quick Start (Fastest Path)

1. **Push to GitHub** (5 min)
2. **Deploy to Railway** (10 min)
3. **Set environment variables** (2 min)
4. **Set up cron job** (2 min)
5. **Load initial data** (5 min)
6. **Test and share!** (2 min)

**Total time: ~25 minutes**

---

## 📞 Need Help?

- Railway Docs: https://docs.railway.app
- Render Docs: https://render.com/docs
- Fly.io Docs: https://fly.io/docs

Your dashboard will be live, accessible, and updating automatically! 🚀

