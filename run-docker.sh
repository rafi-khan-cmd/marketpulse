#!/bin/bash

# MarketPulse Docker Setup Script

set -e

echo "MarketPulse Docker Setup"
echo "============================"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cat > .env << EOF
# Django Settings
DJANGO_SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())" 2>/dev/null || echo "django-insecure-change-me-in-production")
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# API Keys - REPLACE WITH YOUR ACTUAL KEYS
FRED_API_KEY=your-fred-api-key-here
NEWSAPI_KEY=your-newsapi-key-here
EOF
    echo "Created .env file"
    echo ""
    echo " IMPORTANT: Edit .env file and add your API keys:"
    echo "   - FRED_API_KEY (required): https://fred.stlouisfed.org/docs/api/api_key.html"
    echo "   - NEWSAPI_KEY (optional): https://newsapi.org/register"
    echo ""
    read -p "Press Enter to continue after adding your API keys..."
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Docker is not running. Please start Docker and try again."
    exit 1
fi

echo "Building Docker images..."
docker-compose build

echo ""
echo "Starting containers..."
docker-compose up -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 5

echo ""
echo "Running migrations and setting up database..."
docker-compose exec -T web python manage.py migrate

echo ""
echo "Setup complete!"
echo ""
echo "Access the application:"
echo "   - Dashboard: http://localhost:8000/dashboard/"
echo "   - Admin: http://localhost:8000/admin/"
echo "   - API: http://localhost:8000/api/"
echo ""
echo "To load initial data, run:"
echo "   docker-compose exec web python manage.py update_marketpulse"
echo ""
echo "View logs:"
echo "   docker-compose logs -f web"
echo ""
echo "Stop containers:"
echo "   docker-compose down"
echo ""

