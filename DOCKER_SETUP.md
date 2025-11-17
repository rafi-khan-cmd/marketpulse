# Docker Setup Guide for MarketPulse

This guide will help you run MarketPulse using Docker with a complete setup.

## Prerequisites

- Docker installed (https://docs.docker.com/get-docker/)
- Docker Compose installed (usually comes with Docker Desktop)
- FRED API key (get one at https://fred.stlouisfed.org/docs/api/api_key.html)
- NewsAPI key (optional, get one at https://newsapi.org/register)

## Quick Start

### 1. Create Environment File

Create a `.env` file in the project root:

```bash
# Django Settings
DJANGO_SECRET_KEY=your-secret-key-here-generate-a-new-one
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# API Keys
FRED_API_KEY=your-fred-api-key-here
NEWSAPI_KEY=your-newsapi-key-here
```

**To generate a Django secret key:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 2. Build and Start Containers

```bash
docker-compose up --build
```

This will:
- Build the Docker image
- Start PostgreSQL database
- Run migrations
- Start the Django application

### 3. Access the Application

- **Dashboard**: http://localhost:8000/dashboard/
- **Admin Panel**: http://localhost:8000/admin/ (username: `admin`, password: `admin`)
- **API**: http://localhost:8000/api/

### 4. Load Initial Data

In a new terminal, run:

```bash
# Fetch data and train model
docker-compose exec web python manage.py update_marketpulse
```

This will:
- Fetch economic data from FRED
- Fetch market data from Yahoo Finance
- Build feature frames
- Train the ML model
- Fetch and process news articles

**Note**: The first run may take 5-10 minutes as it downloads ML models from Hugging Face.

## Common Commands

### View Logs
```bash
docker-compose logs -f web
```

### Stop Containers
```bash
docker-compose down
```

### Stop and Remove Volumes (clean slate)
```bash
docker-compose down -v
```

### Run Management Commands
```bash
# Update data
docker-compose exec web python manage.py update_marketpulse

# Fetch news only
docker-compose exec web python manage.py fetch_news

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Django shell
docker-compose exec web python manage.py shell
```

### Access Database
```bash
docker-compose exec db psql -U marketpulse_user -d marketpulse
```

## Troubleshooting

### Database Connection Issues

If you see database connection errors, wait a few seconds and try again. The database needs time to initialize.

### Port Already in Use

If port 8000 is already in use, change it in `docker-compose.yml`:
```yaml
ports:
  - "8001:8000"  # Use port 8001 instead
```

### Permission Issues

On Linux, you might need to fix permissions:
```bash
sudo chown -R $USER:$USER .
```

### Rebuild After Code Changes

If you make code changes, rebuild:
```bash
docker-compose up --build
```

### View Container Status
```bash
docker-compose ps
```

## Production Deployment

For production, update your `.env` file:
```bash
DEBUG=False
DJANGO_SECRET_KEY=your-strong-production-secret-key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

And use a reverse proxy (Nginx) in front of the containers.

## Data Persistence

Data is stored in Docker volumes:
- `postgres_data`: Database data
- `static_volume`: Static files

These persist even if you stop the containers. To remove all data:
```bash
docker-compose down -v
```

## Next Steps

1. Set up your API keys in `.env`
2. Build and start containers
3. Load initial data
4. Access the dashboard
5. Set up scheduled tasks (cron) to update data regularly

Enjoy using MarketPulse! 🚀

