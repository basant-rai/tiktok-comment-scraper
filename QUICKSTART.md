# Quick Start Guide

Get started with TikTok Comment Scraper in 5 minutes!

## Option 1: Using Startup Script (Easiest)

### macOS / Linux
```bash
cd tiktok-scrape
chmod +x start.sh
./start.sh
```

### Windows
```bash
cd tiktok-scrape
start.bat
```

The script will:
1. Create a virtual environment (if needed)
2. Install all dependencies
3. Create necessary directories
4. Start the web server

**Then open your browser to:** `http://localhost:5000`

---

## Option 2: Manual Setup

### Step 1: Create Virtual Environment
```bash
python -m venv venv
```

### Step 2: Activate Virtual Environment

**macOS/Linux:**
```bash
source venv/bin/activate
```

**Windows:**
```bash
venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Start the App
```bash
python app.py
```

---

## Using the Web Interface

1. **Enter Video URL**
   - Go to a TikTok video (e.g., `https://www.tiktok.com/@username/video/123456789`)
   - Copy the full URL

2. **Configure Settings**
   - Paste URL in the input field
   - Set max comments (1-10000)
   - Choose export format (JSON/CSV/Excel)

3. **Start Scraping**
   - Click "Start Scraping"
   - Wait for completion

4. **Download Results**
   - Results will appear in the results section
   - Click "Download File" to get your data

---

## First Time Tips

- **First run may take longer** - Playwright/Puppeteer needs to download browser
- **CAPTCHA issues** - If you see CAPTCHA, wait and retry
- **Start small** - Try with 50-100 comments first
- **Check logs** - View `logs/scraper.log` if something goes wrong

---

## Video URL Examples

✅ **Valid URLs:**
```
https://www.tiktok.com/@username/video/7123456789
https://vm.tiktok.com/ZMe1a2b3c/
https://vt.tiktok.com/ZMe1a2b3c/
```

❌ **Invalid URLs:**
```
https://www.tiktok.com/@username (no video)
https://www.tiktok.com/video/123 (incomplete)
```

---

## Common Issues

### Port Already in Use
```bash
PORT=8000 python app.py
```

### Module Not Found
```bash
pip install -r requirements.txt --upgrade
```

### Slow Scraping
- Reduce `max_comments`
- Check your internet connection
- TikTok may be rate limiting

### Browser Issues
Edit `scraper.py`, change `headless=True` to `headless=False` to see what's happening.

---

## Exported Files

Files are saved in the `exports/` folder:
- **JSON** - `comments_YYYYMMDD_HHMMSS.json`
- **CSV** - `comments_YYYYMMDD_HHMMSS.csv`
- **XLSX** - `comments_YYYYMMDD_HHMMSS.xlsx`

All files include:
- ✓ Username & nickname
- ✓ Comment text
- ✓ Likes & reply count
- ✓ Timestamp
- ✓ Verification status
- ✓ Avatar URL

---

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check [API Endpoints](README.md#api-endpoints) to build integrations
- Set up `.env` file for custom configuration

---

## Need Help?

1. Check the logs: `cat logs/scraper.log`
2. Read [README.md](README.md) troubleshooting section
3. Verify your TikTok URL is valid using the web interface
4. Try with a different video or fewer comments

**Happy scraping! 🎵**
