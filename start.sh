#!/bin/bash

echo "🎵 TikTok Comment Scraper - Startup Script"
echo "=========================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "🚀 Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
echo "📥 Installing dependencies..."
pip install -q -r requirements.txt

# Create directories if they don't exist
mkdir -p exports logs

# Start the application
echo ""
echo "✅ Starting TikTok Comment Scraper..."
echo "🌐 Open browser to: http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop the server"
echo "=========================================="
echo ""

python app.py
