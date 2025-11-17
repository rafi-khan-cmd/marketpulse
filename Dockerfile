FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    cron \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Gunicorn
RUN pip install gunicorn

# Copy project
COPY . .

# Create directory for static files and models
RUN mkdir -p /app/staticfiles /app/models

# Make entrypoint script executable
RUN chmod +x docker-entrypoint.sh || true

# Expose port
EXPOSE 8000

# Use entrypoint script
ENTRYPOINT ["./docker-entrypoint.sh"]

# Default command (can be overridden)
# Use PORT environment variable if set (for cloud platforms), otherwise default to 8000
CMD gunicorn --bind 0.0.0.0:${PORT:-8000} --workers 3 server.wsgi:application

