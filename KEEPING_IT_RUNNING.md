# Keeping MarketPulse Running for Resume

## ⚠️ Important: Data Updates Are NOT Automatic

The dashboard will **NOT** update automatically unless you set up scheduled tasks. Here's how to keep it fresh for your resume.

## 🎯 Quick Setup for Automated Updates

### Option 1: Local Cron Job (For Local/Docker Setup)

Run the setup script:
```bash
chmod +x setup_scheduled_updates.sh
./setup_scheduled_updates.sh
```

This will:
- Create an update script
- Schedule daily updates via cron
- Log all updates for monitoring

### Option 2: Docker with Cron (Recommended for Resume)

Add a cron service to `docker-compose.yml`:

```yaml
services:
  # ... existing services ...
  
  cron:
    build: .
    command: >
      sh -c "echo '0 6 * * * cd /app && source venv/bin/activate && 
             export FRED_API_KEY=$$FRED_API_KEY && 
             python manage.py update_marketpulse' | crontab - && 
             crond -f"
    volumes:
      - .:/app
    environment:
      - FRED_API_KEY=${FRED_API_KEY}
      - NEWSAPI_KEY=${NEWSAPI_KEY}
    depends_on:
      - db
      - web
```

### Option 3: Cloud Platform Scheduler (Best for Production)

#### Heroku Scheduler
```bash
# Add to Procfile
worker: python manage.py update_marketpulse

# In Heroku dashboard:
# Resources → Add-ons → Heroku Scheduler
# Schedule: Daily at 6 AM UTC
# Command: python manage.py update_marketpulse
```

#### Railway Cron Jobs
Add `railway.json`:
```json
{
  "cron": {
    "update": {
      "schedule": "0 6 * * *",
      "command": "python manage.py update_marketpulse"
    }
  }
}
```

#### AWS EventBridge / CloudWatch Events
Create a scheduled rule that triggers a Lambda or ECS task.

## 📊 Update Frequency Recommendations

**For Resume/Portfolio:**
- **Minimum**: Daily at 6 AM (before business hours)
- **Recommended**: Twice daily (6 AM and 6 PM)
- **Best**: Every 6 hours for near real-time data

**What Gets Updated:**
- Economic data from FRED (CPI, unemployment, rates)
- Market data from Yahoo Finance (SPX, VIX, volume)
- News articles from NewsAPI
- ML model retraining (if you want fresh predictions)

## 🔍 Monitoring & Verification

### Check if Updates Are Running

```bash
# View cron logs
tail -f logs/update.log

# Check last update time
docker-compose exec web python manage.py shell -c "
from core.models import FeatureFrame
ff = FeatureFrame.objects.order_by('-date').first()
print(f'Last data: {ff.date if ff else \"None\"}')"
```

### Manual Update (For Testing)

```bash
# Local
source venv/bin/activate
python manage.py update_marketpulse

# Docker
docker-compose exec web python manage.py update_marketpulse
```

## 🚀 Deployment Options for Resume

### Option A: Free Hosting (Recommended)

**Railway.app** (Free tier available):
- Automatic deployments from GitHub
- Built-in cron jobs
- PostgreSQL included
- Easy to set up

**Render.com** (Free tier):
- Automatic deployments
- Cron jobs available
- PostgreSQL included

**Fly.io** (Free tier):
- Good for Docker deployments
- Can run scheduled tasks

### Option B: Always-On Server

If you have a VPS or always-on machine:
- Use the cron setup script
- Ensure Docker containers restart on reboot
- Monitor with health checks

### Option C: Cloud Functions (Advanced)

Use serverless functions:
- AWS Lambda + EventBridge
- Google Cloud Functions + Cloud Scheduler
- Azure Functions + Timer Trigger

## ⚙️ Docker Setup for Always-On

### Ensure Containers Restart

Your `docker-compose.yml` already has:
```yaml
restart: unless-stopped
```

This ensures containers restart if they crash.

### Auto-start on Boot (Linux)

```bash
# Create systemd service
sudo nano /etc/systemd/system/marketpulse.service
```

Add:
```ini
[Unit]
Description=MarketPulse Docker Compose
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/path/to/marketpulse
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
User=your-username

[Install]
WantedBy=multi-user.target
```

Enable:
```bash
sudo systemctl enable marketpulse
sudo systemctl start marketpulse
```

## 📝 Resume Link Best Practices

### What to Include

✅ **Good:**
- "Live demo: [your-link]" 
- "View dashboard: [your-link]"
- "Portfolio project: [your-link]"

❌ **Avoid:**
- "Check it out" (too casual)
- Just the link without context

### Link Format

```
https://your-app.railway.app/dashboard/
or
https://marketpulse.herokuapp.com/dashboard/
```

### Add a Note

In your resume or portfolio:
> "Note: Data updates daily at 6 AM EST. Dashboard may take a moment to load on first visit."

## 🔧 Quick Checklist Before Sharing

- [ ] Data updates are scheduled (cron/cloud scheduler)
- [ ] Containers have restart policy
- [ ] Environment variables are set
- [ ] API keys are valid
- [ ] Test the link yourself
- [ ] Check on mobile device
- [ ] Verify all charts load
- [ ] Check news feed works
- [ ] Test prediction endpoint

## 🆘 Troubleshooting

### Data Looks Stale

```bash
# Check last update
docker-compose exec web python manage.py shell -c "
from core.models import FeatureFrame, NewsArticle
print('Last feature:', FeatureFrame.objects.order_by('-date').first().date)
print('Last news:', NewsArticle.objects.order_by('-published_at').first().published_at)"
```

### Updates Not Running

1. Check cron is running: `crontab -l`
2. Check logs: `tail -f logs/update.log`
3. Test manually: `python manage.py update_marketpulse`
4. Check API keys are set

### Dashboard Not Loading

1. Check containers: `docker-compose ps`
2. Check logs: `docker-compose logs web`
3. Verify port is accessible
4. Check ALLOWED_HOSTS in settings

## 💡 Pro Tips

1. **Set up monitoring**: Use UptimeRobot or Pingdom to alert if site goes down
2. **Backup data**: Regularly backup your database
3. **Document setup**: Keep notes on how to restart/update
4. **Test regularly**: Check the link weekly to ensure it works
5. **Update dependencies**: Keep packages updated for security

## 📞 Quick Commands Reference

```bash
# Manual update
docker-compose exec web python manage.py update_marketpulse

# Check status
docker-compose ps

# View logs
docker-compose logs -f web

# Restart everything
docker-compose restart

# Check last data update
docker-compose exec web python manage.py shell -c "
from core.models import FeatureFrame
print(FeatureFrame.objects.order_by('-date').first().date)"
```

---

**Remember**: For a resume project, daily updates are usually sufficient. Set it up once, and it will keep your dashboard fresh automatically! 🚀

