@echo off
echo 🎵 TikTok Comment Scraper - Startup Script
echo ==========================================
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🚀 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/upgrade dependencies
echo 📥 Installing dependencies...
pip install -q -r requirements.txt

REM Create directories if they don't exist
if not exist "exports" mkdir exports
if not exist "logs" mkdir logs

REM Start the application
echo.
echo ✅ Starting TikTok Comment Scraper...
echo 🌐 Open browser to: http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo ==========================================
echo.

python app.py
pause
