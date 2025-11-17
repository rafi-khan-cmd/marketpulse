# Complete Docker Guide: Start & Stop MarketPulse

## 🚀 COMPLETE START PROCESS

### Step 1: Verify Docker is Running

```bash
# Check if Docker is running
docker ps
```

If you see an error, start Docker Desktop:
- Open **Docker Desktop** application on your Mac
- Wait for the whale icon in the menu bar to be steady (not animated)

### Step 2: Navigate to Project Directory

```bash
cd /Users/rafiulalamkhan/MarketPulseCursor/marketpulse
```

### Step 3: Verify Environment File

```bash
# Check if .env file exists and has your API keys
cat .env
```

You should see:
```
FRED_API_KEY=43e833b6295bbba47d543d7a70ff7b5c
```

### Step 4: Build Docker Images (First Time Only)

```bash
# Build the Docker images
docker-compose build
```

**Expected output:**
```
Building web...
Step 1/10 : FROM python:3.11-slim
...
Successfully built abc123def456
```

**Time:** 2-5 minutes (first time only)

### Step 5: Start All Services

```bash
# Start PostgreSQL and Django in detached mode
docker-compose up -d
```

**Expected output:**
```
Creating network "marketpulse_default" ... done
Creating marketpulse_db_1 ... done
Creating marketpulse_web_1 ... done
```

### Step 6: Check Service Status

```bash
# View running containers
docker-compose ps
```

**Expected output:**
```
NAME                COMMAND                  STATUS          PORTS
marketpulse_db_1    "docker-entrypoint.s…"   Up (healthy)    5432/tcp
marketpulse_web_1   "./docker-entrypoint…"   Up              0.0.0.0:8000->8000/tcp
```

### Step 7: View Logs (Optional but Recommended)

```bash
# Watch the logs to see startup progress
docker-compose logs -f web
```

**What to look for:**
- ✅ "Database is ready!"
- ✅ "Running migrations..."
- ✅ "Starting server..."
- ✅ "Booting worker with pid: X"

Press `Ctrl+C` to stop watching logs (containers keep running)

### Step 8: Wait for Services to be Ready

Wait about 30 seconds, then verify:

```bash
# Check if web service is responding
curl http://localhost:8000/api/timeseries/?code=SPX_CLOSE
```

Or open in browser: http://localhost:8000/dashboard/

### Step 9: Load Initial Data (First Time)

```bash
# Fetch data from APIs and train ML model
docker-compose exec web python manage.py update_marketpulse
```

**What this does:**
1. Fetches economic data from FRED
2. Fetches market data from Yahoo Finance
3. Builds feature frames
4. Trains ML model
5. Fetches and processes news

**Time:** 5-10 minutes (first time, downloads ML models)

**Expected output:**
```
1) FRED macro ETL
Fetching CPIAUCSL -> CPI ...
 -> stored 945 rows for CPI
...
✅ MarketPulse update pipeline completed.
```

### Step 10: Access the Application

**Dashboard:**
```
http://localhost:8000/dashboard/
```

**Admin Panel:**
```
http://localhost:8000/admin/
```

**API Endpoints:**
```
http://localhost:8000/api/timeseries/?code=SPX_CLOSE
http://localhost:8000/api/macro-snapshot/
http://localhost:8000/api/news/
http://localhost:8000/api/spx-direction/
```

---

## 🛑 COMPLETE STOP PROCESS

### Option 1: Stop Containers (Keep Data)

```bash
# Stop all running containers
docker-compose stop
```

**What this does:**
- Stops containers but keeps them
- Preserves all data in database
- Can restart quickly with `docker-compose start`

**Verify:**
```bash
docker-compose ps
# Should show "Exited" status
```

### Option 2: Stop and Remove Containers (Keep Data)

```bash
# Stop and remove containers
docker-compose down
```

**What this does:**
- Stops containers
- Removes containers
- **Keeps database data** (stored in volumes)
- **Keeps code changes**

**Verify:**
```bash
docker-compose ps
# Should show "no containers"
```

### Option 3: Complete Cleanup (Remove Everything)

```bash
# Stop, remove containers, AND delete all data
docker-compose down -v
```

**⚠️ WARNING:** This deletes:
- All database data
- All uploaded files
- All volumes

**Use this when:**
- Starting completely fresh
- Troubleshooting persistent issues
- Before production deployment

---

## 🔄 RESTART PROCESS

### Quick Restart (After Stop)

```bash
# If you used 'docker-compose stop'
docker-compose start

# If you used 'docker-compose down'
docker-compose up -d
```

### Full Restart (Rebuild)

```bash
# Stop everything
docker-compose down

# Rebuild (if code changed)
docker-compose build

# Start again
docker-compose up -d
```

---

## 📋 USEFUL COMMANDS

### View Logs

```bash
# All services
docker-compose logs

# Just web service
docker-compose logs web

# Follow logs (real-time)
docker-compose logs -f web

# Last 100 lines
docker-compose logs --tail=100 web
```

### Execute Commands in Container

```bash
# Django shell
docker-compose exec web python manage.py shell

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Update data
docker-compose exec web python manage.py update_marketpulse

# Fetch news
docker-compose exec web python manage.py fetch_news
```

### Database Access

```bash
# PostgreSQL shell
docker-compose exec db psql -U marketpulse_user -d marketpulse

# Common SQL commands:
# \dt          - List tables
# \d table_name - Describe table
# SELECT * FROM core_series LIMIT 10;
# \q           - Quit
```

### Container Management

```bash
# View running containers
docker-compose ps

# View all containers (including stopped)
docker-compose ps -a

# Restart a specific service
docker-compose restart web

# View resource usage
docker stats

# View container details
docker-compose exec web env
```

### Troubleshooting

```bash
# Check if port is in use
lsof -i :8000

# View container logs for errors
docker-compose logs web | grep -i error

# Restart everything
docker-compose restart

# Rebuild without cache
docker-compose build --no-cache

# Remove and recreate containers
docker-compose down
docker-compose up -d --force-recreate
```

---

## 📊 QUICK REFERENCE

### Start Everything
```bash
docker-compose up -d
```

### Stop Everything (Keep Data)
```bash
docker-compose down
```

### View Logs
```bash
docker-compose logs -f web
```

### Load Data
```bash
docker-compose exec web python manage.py update_marketpulse
```

### Access Dashboard
```
http://localhost:8000/dashboard/
```

---

## ✅ VERIFICATION CHECKLIST

After starting, verify:

- [ ] Containers are running: `docker-compose ps`
- [ ] Web service is up: `curl http://localhost:8000/`
- [ ] Database is connected: Check logs for "Database is ready!"
- [ ] Migrations ran: Check logs for "Running migrations..."
- [ ] Dashboard loads: http://localhost:8000/dashboard/
- [ ] Data is loaded: Run `update_marketpulse` command

---

## 🆘 TROUBLESHOOTING

### "Cannot connect to Docker daemon"
- Start Docker Desktop
- Wait for it to fully start

### "Port 8000 already in use"
```bash
# Find what's using the port
lsof -i :8000

# Kill the process or change port in docker-compose.yml
```

### "Database connection failed"
- Wait longer (database needs 30-60 seconds to initialize)
- Check database logs: `docker-compose logs db`

### "No such service: web"
- Make sure you're in the project directory
- Run `docker-compose up -d` first

### Containers keep restarting
- Check logs: `docker-compose logs web`
- Look for errors in startup
- Try rebuilding: `docker-compose build --no-cache`

---

That's it! You now have complete control over starting and stopping MarketPulse with Docker! 🎉

