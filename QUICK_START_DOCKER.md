# Quick Start: Docker Setup

## Step 1: Start Docker Desktop

Make sure Docker Desktop is running on your Mac. If not:
1. Open Docker Desktop application
2. Wait for it to fully start (whale icon in menu bar should be steady)

## Step 2: Build and Run

```bash
# Build the Docker images
docker-compose build

# Start all services
docker-compose up -d

# View logs to see progress
docker-compose logs -f web
```

## Step 3: Wait for Services

Wait about 30 seconds for:
- PostgreSQL database to initialize
- Django migrations to run
- Server to start

## Step 4: Load Initial Data

Once the containers are running, load data:

```bash
docker-compose exec web python manage.py update_marketpulse
```

**Note**: This will take 5-10 minutes the first time as it downloads ML models.

## Step 5: Access the Application

- **Dashboard**: http://localhost:8000/dashboard/
- **Admin Panel**: http://localhost:8000/admin/
- **API**: http://localhost:8000/api/

## Common Commands

```bash
# View logs
docker-compose logs -f web

# Stop containers
docker-compose down

# Restart containers
docker-compose restart

# Run commands in container
docker-compose exec web python manage.py shell
docker-compose exec web python manage.py createsuperuser

# View container status
docker-compose ps
```

## Troubleshooting

### Port 8000 already in use
Change the port in `docker-compose.yml`:
```yaml
ports:
  - "8001:8000"  # Use 8001 instead
```

### Database connection errors
Wait a bit longer - the database needs time to initialize. Check logs:
```bash
docker-compose logs db
```

### Rebuild after changes
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## Your .env File

Your `.env` file is already configured with:
- FRED_API_KEY: ✅ Set
- NEWSAPI_KEY: (optional, can add later)

You're all set! 🚀

