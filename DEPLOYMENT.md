# Deployment Guide

This guide covers deploying MarketPulse to production environments.

## Prerequisites

- Python 3.11+
- PostgreSQL (recommended) or MySQL for production
- Web server (Nginx, Apache, or cloud platform)
- Application server (Gunicorn, uWSGI, or cloud platform)

## Environment Variables

Create a `.env` file or set environment variables:

```bash
# Django Settings
DJANGO_SECRET_KEY=your-production-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# API Keys
FRED_API_KEY=your-fred-api-key
NEWSAPI_KEY=your-newsapi-key

# Database (PostgreSQL example)
DATABASE_URL=postgresql://user:password@localhost:5432/marketpulse
```

**Important**: Generate a new SECRET_KEY for production:
```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

## Database Setup

### PostgreSQL (Recommended)

1. Install PostgreSQL:
```bash
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# macOS
brew install postgresql
```

2. Create database and user:
```sql
CREATE DATABASE marketpulse;
CREATE USER marketpulse_user WITH PASSWORD 'your_password';
ALTER ROLE marketpulse_user SET client_encoding TO 'utf8';
ALTER ROLE marketpulse_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE marketpulse_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE marketpulse TO marketpulse_user;
```

3. Update `settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'marketpulse'),
        'USER': os.getenv('DB_USER', 'marketpulse_user'),
        'PASSWORD': os.getenv('DB_PASSWORD', ''),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}
```

4. Install PostgreSQL adapter:
```bash
pip install psycopg2-binary
```

## Static Files

1. Update `settings.py`:
```python
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATIC_URL = '/static/'
```

2. Collect static files:
```bash
python manage.py collectstatic --noinput
```

## Deployment Options

### Option 1: Docker Deployment

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Run with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "server.wsgi:application"]
```

Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: marketpulse
      POSTGRES_USER: marketpulse_user
      POSTGRES_PASSWORD: your_password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  web:
    build: .
    command: gunicorn --bind 0.0.0.0:8000 server.wsgi:application
    volumes:
      - .:/app
      - static_volume:/app/staticfiles
    ports:
      - "8000:8000"
    environment:
      - DJANGO_SECRET_KEY=your-secret-key
      - FRED_API_KEY=your-fred-key
      - NEWSAPI_KEY=your-newsapi-key
      - DATABASE_URL=postgresql://marketpulse_user:your_password@db:5432/marketpulse
    depends_on:
      - db

volumes:
  postgres_data:
  static_volume:
```

Deploy:
```bash
docker-compose up -d
```

### Option 2: Gunicorn + Nginx

1. Install Gunicorn:
```bash
pip install gunicorn
```

2. Create Gunicorn service file `/etc/systemd/system/marketpulse.service`:
```ini
[Unit]
Description=MarketPulse Gunicorn daemon
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/marketpulse
ExecStart=/path/to/venv/bin/gunicorn \
    --access-logfile - \
    --workers 3 \
    --bind unix:/run/gunicorn.sock \
    server.wsgi:application

[Install]
WantedBy=multi-user.target
```

3. Create Nginx configuration `/etc/nginx/sites-available/marketpulse`:
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location /static/ {
        alias /path/to/marketpulse/staticfiles/;
    }

    location / {
        proxy_pass http://unix:/run/gunicorn.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

4. Enable and start services:
```bash
sudo systemctl enable marketpulse
sudo systemctl start marketpulse
sudo systemctl restart nginx
```

### Option 3: Cloud Platforms

#### Heroku

1. Create `Procfile`:
```
web: gunicorn server.wsgi:application
worker: python manage.py update_marketpulse --schedule
```

2. Create `runtime.txt`:
```
python-3.11.9
```

3. Deploy:
```bash
heroku create marketpulse-app
heroku config:set DJANGO_SECRET_KEY=your-secret-key
heroku config:set FRED_API_KEY=your-fred-key
heroku addons:create heroku-postgresql:hobby-dev
git push heroku main
```

#### Railway

1. Add `railway.json`:
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "gunicorn server.wsgi:application",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

#### AWS Elastic Beanstalk

1. Create `.ebextensions/django.config`:
```yaml
option_settings:
  aws:elasticbeanstalk:container:python:
    WSGIPath: server.wsgi:application
```

2. Deploy:
```bash
eb init
eb create marketpulse-env
eb deploy
```

## Scheduled Tasks

Set up cron jobs or scheduled tasks for data updates:

```bash
# Update data daily at 6 AM
0 6 * * * cd /path/to/marketpulse && /path/to/venv/bin/python manage.py update_marketpulse
```

Or use Celery for more advanced task scheduling (requires additional setup).

## Security Checklist

- [ ] Set `DEBUG=False` in production
- [ ] Use strong `SECRET_KEY` from environment variable
- [ ] Configure `ALLOWED_HOSTS` properly
- [ ] Use HTTPS (SSL/TLS certificates)
- [ ] Set secure cookie flags
- [ ] Use PostgreSQL or MySQL (not SQLite)
- [ ] Set up proper firewall rules
- [ ] Keep dependencies updated
- [ ] Use environment variables for all secrets
- [ ] Set up logging and monitoring
- [ ] Configure backup strategy

## Monitoring

Consider setting up:
- Application monitoring (Sentry, Rollbar)
- Server monitoring (New Relic, Datadog)
- Log aggregation (ELK stack, CloudWatch)
- Uptime monitoring (Pingdom, UptimeRobot)

## Backup Strategy

1. Database backups:
```bash
# PostgreSQL
pg_dump marketpulse > backup_$(date +%Y%m%d).sql

# Automated daily backup
0 2 * * * pg_dump marketpulse | gzip > /backups/marketpulse_$(date +\%Y\%m\%d).sql.gz
```

2. Model artifacts: Backup `models/` directory
3. Static files: Backup `staticfiles/` directory

## Performance Optimization

1. Enable caching (Redis/Memcached)
2. Use CDN for static files
3. Database query optimization
4. Enable database connection pooling
5. Use async tasks for ETL (Celery)

## Troubleshooting

### Common Issues

1. **Static files not loading**: Run `collectstatic` and check `STATIC_ROOT`
2. **Database connection errors**: Verify credentials and network access
3. **Permission errors**: Check file permissions and user/group settings
4. **API key errors**: Verify environment variables are set correctly

### Logs

Check logs:
```bash
# Gunicorn logs
journalctl -u marketpulse

# Nginx logs
tail -f /var/log/nginx/error.log

# Django logs
tail -f /path/to/marketpulse/logs/django.log
```

## Support

For issues or questions, refer to:
- Django deployment docs: https://docs.djangoproject.com/en/stable/howto/deployment/
- Gunicorn docs: https://docs.gunicorn.org/
- Nginx docs: https://nginx.org/en/docs/

