#!/bin/bash
set -e

echo "🚀 Starting MarketPulse container..."
echo "🔍 Environment check:"
echo "   FRED_API_KEY: ${FRED_API_KEY:+SET (length: ${#FRED_API_KEY})}"
echo "   NEWSAPI_KEY: ${NEWSAPI_KEY:+SET (length: ${#NEWSAPI_KEY})}"
echo "   DATABASE_URL: ${DATABASE_URL:+SET}"
echo "   PORT: ${PORT:-NOT SET}"

echo "Waiting for database to be ready..."
python << END
import sys
import time
import os

try:
    import psycopg2
    db_url = os.getenv('DATABASE_URL', '')
    if db_url:
        max_attempts = 30
        attempt = 0
        while attempt < max_attempts:
            try:
                conn = psycopg2.connect(db_url)
                conn.close()
                print("Database is ready!")
                sys.exit(0)
            except psycopg2.OperationalError:
                attempt += 1
                print(f"Waiting for database... ({attempt}/{max_attempts})")
                time.sleep(2)
        print("Database connection failed after 30 attempts")
        sys.exit(1)
except ImportError:
    print("psycopg2 not available, skipping database check")
    sys.exit(0)
END

echo "Running migrations..."
python manage.py migrate --noinput || {
    echo "WARNING: Migrations failed, but continuing..."
}

echo "Collecting static files..."
python manage.py collectstatic --noinput || true

echo "Starting server..."
exec "$@"

