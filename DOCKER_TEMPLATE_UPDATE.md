# Updating Dashboard Template in Docker

## Quick Answer: **NO full rebuild needed!**

Since your code is mounted as a volume in `docker-compose.yml`, template changes are automatically available.

## Option 1: Just Refresh Browser (Usually Works)

1. **Hard refresh your browser:**
   - **Chrome/Firefox**: `Ctrl+Shift+R` (Windows) or `Cmd+Shift+R` (Mac)
   - Or open DevTools (F12) and right-click refresh → "Empty Cache and Hard Reload"

2. **That's it!** The template file is already updated in the container.

## Option 2: Restart Web Container (If Option 1 Doesn't Work)

If you still see the old design after hard refresh:

```bash
# Restart just the web container (takes 5 seconds)
docker-compose restart web

# Then refresh browser
```

## Option 3: Full Rebuild (Only if Needed)

Only needed if:
- You changed Python dependencies (`requirements.txt`)
- You changed Dockerfile
- You changed Django settings that require rebuild

```bash
# Stop containers
docker-compose down

# Rebuild (this takes 2-5 minutes)
docker-compose build

# Start again
docker-compose up -d
```

## Why This Works

Your `docker-compose.yml` has:
```yaml
volumes:
  - .:/app  # This mounts your local code into the container
```

This means:
- ✅ Template changes (`dashboard.html`) → **No restart needed**
- ✅ Python code changes → **No restart needed** (but restart recommended)
- ✅ Settings changes → **Restart needed**
- ✅ Requirements changes → **Rebuild needed**

## Quick Commands Reference

```bash
# See if containers are running
docker-compose ps

# Restart web container (fast)
docker-compose restart web

# View logs to see if it's working
docker-compose logs -f web

# Full rebuild (slow, only when needed)
docker-compose down
docker-compose build
docker-compose up -d
```

## Troubleshooting

**If changes don't appear:**

1. **Check if file was saved:**
   ```bash
   # Verify the file exists and has new content
   cat core/templates/core/dashboard.html | head -20
   ```

2. **Check if container is running:**
   ```bash
   docker-compose ps
   ```

3. **Check Django template cache:**
   ```bash
   # Restart web container to clear cache
   docker-compose restart web
   ```

4. **Check browser cache:**
   - Open in incognito/private window
   - Or clear browser cache completely

## Summary

For **template/HTML changes**: Just **hard refresh browser** (Ctrl+Shift+R)

For **Python code changes**: **Restart web container** (`docker-compose restart web`)

For **dependency/settings changes**: **Rebuild** (`docker-compose build`)

