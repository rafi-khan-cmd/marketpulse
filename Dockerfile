FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies (minimal - only what's needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    cron \
    build-essential \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean \
    && rm -rf /tmp/* /var/tmp/*

# Install Python dependencies (CPU-only PyTorch to save space)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir torch==2.3.1 --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get purge -y build-essential gcc g++ && \
    apt-get autoremove -y

# Copy only necessary project files (excludes docs via .dockerignore)
COPY . .

# Create directory for static files and models
RUN mkdir -p /app/staticfiles /app/models

# Make entrypoint script executable
RUN chmod +x docker-entrypoint.sh || true

# Clean up Python cache
RUN find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true && \
    find . -type f -name "*.pyc" -delete

# Expose port
EXPOSE 8000

# Use entrypoint script
ENTRYPOINT ["./docker-entrypoint.sh"]

# Default command (can be overridden)
# Railway sets PORT automatically, use shell to expand it
CMD sh -c "gunicorn --bind 0.0.0.0:${PORT:-8000} --workers 3 server.wsgi:application"

