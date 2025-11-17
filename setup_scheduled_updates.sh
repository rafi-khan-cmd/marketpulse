#!/bin/bash

# Setup script for automated data updates
# This creates a cron job to update MarketPulse data regularly

echo "🔄 MarketPulse Automated Updates Setup"
echo "======================================"
echo ""

# Check if running in Docker
if [ -f /.dockerenv ] || [ -n "$DOCKER_CONTAINER" ]; then
    echo "📦 Detected Docker environment"
    echo ""
    echo "For Docker, you have two options:"
    echo ""
    echo "Option 1: Use Docker's restart policy + cron inside container"
    echo "Option 2: Use external cron on host machine"
    echo ""
    echo "Recommended: Use a cloud scheduler (see DEPLOYMENT.md)"
    echo ""
    exit 0
fi

# Get the project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PATH="$PROJECT_DIR/venv"

echo "Project directory: $PROJECT_DIR"
echo ""

# Check if virtual environment exists
if [ ! -d "$VENV_PATH" ]; then
    echo "❌ Virtual environment not found at $VENV_PATH"
    echo "Please create it first: python3 -m venv venv"
    exit 1
fi

# Create update script
UPDATE_SCRIPT="$PROJECT_DIR/update_data.sh"
cat > "$UPDATE_SCRIPT" << 'EOF'
#!/bin/bash
# MarketPulse automated data update script

cd /Users/rafiulalamkhan/MarketPulseCursor/marketpulse
source venv/bin/activate
export FRED_API_KEY="43e833b6295bbba47d543d7a70ff7b5c"
export NEWSAPI_KEY="${NEWSAPI_KEY:-}"

python manage.py update_marketpulse >> logs/update.log 2>&1
EOF

chmod +x "$UPDATE_SCRIPT"

# Create logs directory
mkdir -p "$PROJECT_DIR/logs"

echo "✅ Created update script: $UPDATE_SCRIPT"
echo ""

# Ask user for update frequency
echo "How often should data be updated?"
echo "1) Daily at 6 AM"
echo "2) Daily at 9 AM (market open)"
echo "3) Twice daily (6 AM and 6 PM)"
echo "4) Every 6 hours"
echo "5) Custom (you'll edit cron manually)"
echo ""
read -p "Choose option (1-5): " choice

case $choice in
    1)
        CRON_SCHEDULE="0 6 * * *"
        DESC="Daily at 6 AM"
        ;;
    2)
        CRON_SCHEDULE="0 9 * * *"
        DESC="Daily at 9 AM"
        ;;
    3)
        CRON_SCHEDULE="0 6,18 * * *"
        DESC="Twice daily (6 AM and 6 PM)"
        ;;
    4)
        CRON_SCHEDULE="0 */6 * * *"
        DESC="Every 6 hours"
        ;;
    5)
        echo ""
        echo "To add custom schedule, edit crontab:"
        echo "  crontab -e"
        echo ""
        echo "Add this line:"
        echo "  * * * * * $UPDATE_SCRIPT"
        echo ""
        echo "Cron format: minute hour day month weekday"
        echo "Example: 0 6 * * * = daily at 6 AM"
        exit 0
        ;;
    *)
        echo "Invalid choice. Using default: Daily at 6 AM"
        CRON_SCHEDULE="0 6 * * *"
        DESC="Daily at 6 AM"
        ;;
esac

# Add to crontab
(crontab -l 2>/dev/null | grep -v "$UPDATE_SCRIPT"; echo "$CRON_SCHEDULE $UPDATE_SCRIPT") | crontab -

echo ""
echo "✅ Scheduled task added!"
echo "   Schedule: $DESC"
echo "   Command: $UPDATE_SCRIPT"
echo ""
echo "📋 View scheduled tasks:"
echo "   crontab -l"
echo ""
echo "📝 View update logs:"
echo "   tail -f $PROJECT_DIR/logs/update.log"
echo ""
echo "🛑 Remove scheduled task:"
echo "   crontab -e  (then delete the line)"
echo ""

