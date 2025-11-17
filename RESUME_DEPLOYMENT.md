# Deploying MarketPulse for Resume - Complete Guide

## 🎯 Goal: Keep Your Dashboard Fresh and Accessible

When you put a link on your resume, it needs to:
- ✅ Be accessible 24/7
- ✅ Update data automatically
- ✅ Look professional
- ✅ Load quickly

## 🚀 Recommended: Deploy to Cloud Platform

### Option 1: Railway.app (Easiest & Free Tier Available)

**Why Railway:**
- Free tier with 500 hours/month
- Automatic deployments from GitHub
- Built-in PostgreSQL
- Easy cron job setup
- Custom domain support

**Steps:**

1. **Push to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin your-github-repo-url
   git push -u origin main
   ```

2. **Deploy on Railway:**
   - Go to https://railway.app
   - Sign up with GitHub
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your MarketPulse repo
   - Railway auto-detects Docker

3. **Add PostgreSQL:**
   - Click "+ New" → "Database" → "PostgreSQL"
   - Railway auto-sets `DATABASE_URL`

4. **Set Environment Variables:**
   - Go to your service → Variables
   - Add:
     ```
     FRED_API_KEY=43e833b6295bbba47d543d7a70ff7b5c
     NEWSAPI_KEY=your-newsapi-key
     DJANGO_SECRET_KEY=generate-new-secret-key
     DEBUG=False
     ALLOWED_HOSTS=your-app.railway.app
     ```

5. **Set Up Cron Job:**
   - Add `railway.json` to your repo:
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
   - Use Railway's Cron Jobs feature (in dashboard)
   - Schedule: `0 6 * * *` (daily at 6 AM UTC)
   - Command: `python manage.py update_marketpulse`

6. **Get Your URL:**
   - Railway provides: `https://your-app.railway.app`
   - Add `/dashboard/` for the dashboard

### Option 2: Render.com (Free Tier)

**Steps:**

1. **Connect GitHub repo** to Render

2. **Create Web Service:**
   - Environment: Docker
   - Build Command: (auto-detected)
   - Start Command: `gunicorn --bind 0.0.0.0:$PORT --workers 3 server.wsgi:application`

3. **Add PostgreSQL Database:**
   - Create PostgreSQL service
   - Render auto-sets `DATABASE_URL`

4. **Set Environment Variables:**
   - Same as Railway above

5. **Set Up Cron Job:**
   - Create a "Background Worker" service
   - Command: `python manage.py update_marketpulse`
   - Schedule: Daily at 6 AM

### Option 3: Fly.io (Good for Docker)

**Steps:**

1. **Install Fly CLI:**
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. **Create `fly.toml`:**
   ```toml
   app = "your-app-name"
   primary_region = "iad"

   [build]
     dockerfile = "Dockerfile"

   [http_service]
     internal_port = 8000
     force_https = true
     auto_stop_machines = false
     auto_start_machines = true
     min_machines_running = 1

   [[services]]
     internal_port = 8000
     protocol = "tcp"
   ```

3. **Deploy:**
   ```bash
   fly launch
   fly secrets set FRED_API_KEY=43e833b6295bbba47d543d7a70ff7b5c
   fly secrets set NEWSAPI_KEY=your-key
   fly secrets set DJANGO_SECRET_KEY=your-secret
   ```

4. **Set Up Cron:**
   - Use Fly's scheduled tasks or external cron service

## 📋 Pre-Deployment Checklist

Before deploying, ensure:

- [ ] All environment variables are set
- [ ] `DEBUG=False` in production
- [ ] `ALLOWED_HOSTS` includes your domain
- [ ] `SECRET_KEY` is generated (not default)
- [ ] Database migrations are ready
- [ ] Static files collection works
- [ ] Docker builds successfully
- [ ] Tests pass

## 🔄 Automated Updates Setup

### For Docker (Local/Server)

Your `docker-compose.yml` now includes a `scheduler` service that:
- Runs daily at 6 AM UTC
- Updates all data automatically
- Logs to `logs/cron.log`

**To use it:**
```bash
docker-compose up -d
```

The scheduler will automatically update data daily.

### For Cloud Platforms

Most platforms have built-in cron/scheduler:
- **Railway**: Cron Jobs in dashboard
- **Render**: Background Workers
- **Heroku**: Heroku Scheduler add-on
- **Fly.io**: Use external service or scheduled tasks

## 🔍 Monitoring Your Deployment

### Check if Updates Are Working

```bash
# View update logs
docker-compose logs scheduler

# Or in cloud platform, check logs
```

### Verify Data is Fresh

Visit your dashboard and check:
- Latest news date (should be recent)
- Chart data (should show recent dates)
- Macro snapshot date

### Set Up Alerts (Optional but Recommended)

Use free services:
- **UptimeRobot**: Monitors if site is down
- **Pingdom**: Uptime monitoring
- **StatusCake**: Free monitoring

## 📝 Resume Link Format

**Good Examples:**
```
Live Demo: https://marketpulse.railway.app/dashboard/
Portfolio Project: https://your-app.render.com/dashboard/
```

**What to Say:**
> "MarketPulse - Financial Market Analysis Platform
> Live demo: [your-link]
> (Data updates daily at 6 AM EST)"

## ⚠️ Important Notes

1. **Free tiers have limits:**
   - Railway: 500 hours/month (enough for always-on)
   - Render: Sleeps after 15 min inactivity (upgrade for always-on)
   - Fly.io: Limited free tier

2. **API Rate Limits:**
   - FRED: Free tier is generous
   - NewsAPI: Free tier = 100 requests/day
   - yfinance: No API key needed

3. **Cost Considerations:**
   - Most platforms offer free tiers
   - PostgreSQL is usually included
   - Only pay if you exceed limits

## 🛠️ Troubleshooting

### Site Not Loading

1. Check deployment logs
2. Verify environment variables
3. Check `ALLOWED_HOSTS` includes your domain
4. Ensure database is connected

### Data Not Updating

1. Check cron job is scheduled
2. View cron logs
3. Test manual update: `python manage.py update_marketpulse`
4. Verify API keys are set

### Database Issues

1. Check database connection string
2. Run migrations: `python manage.py migrate`
3. Verify database is running

## 🎯 Quick Start for Resume

**Fastest Path:**

1. Push code to GitHub
2. Deploy to Railway.app (easiest)
3. Set environment variables
4. Enable cron job for daily updates
5. Test the link
6. Add to resume!

**Time to deploy:** ~15 minutes

**Cost:** Free (on free tiers)

**Maintenance:** Minimal (just check monthly)

---

## ✅ Final Checklist Before Sharing Link

- [ ] Dashboard loads correctly
- [ ] All charts display data
- [ ] News feed shows articles
- [ ] Prediction shows values
- [ ] Data is recent (within 24 hours)
- [ ] Site is accessible from different networks
- [ ] Mobile view works
- [ ] No errors in browser console
- [ ] API endpoints work
- [ ] Cron job is scheduled

**Once all checked, you're ready to share!** 🚀

