# TikTok Comment Scraper

A production-ready web application for scraping and analyzing comments from TikTok videos.

## Features

✨ **Core Features**
- 🎯 Scrape comments from any TikTok video URL
- 📊 Real-time comment extraction with progress tracking
- 💾 Multiple export formats (JSON, CSV, Excel)
- 🔍 URL validation and video ID extraction
- ⚡ Async/concurrent scraping for better performance
- 🔄 Automatic retry mechanism for failed scrapes
- 📈 Statistical analysis of comments
- 🎨 Modern, responsive web UI
- 📝 Comprehensive logging system

## Data Extracted

Each comment includes:
- **ID**: Unique comment identifier
- **Username**: Creator's username
- **Nickname**: Display name
- **Avatar URL**: Profile picture link
- **Text**: Comment content
- **Likes**: Engagement count
- **Replies**: Number of replies to comment
- **Created At**: Timestamp
- **User Verified**: Verification status

## Installation

### Prerequisites
- Python 3.8+
- Virtual environment (recommended)

### Setup

```bash
# Clone/navigate to project directory
cd tiktok-scrape

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the project root (optional):

```env
DEBUG=False
HOST=127.0.0.1
PORT=5000
HEADLESS=True
OUTPUT_DIR=exports
LOGS_DIR=logs
```

## Usage

### Web Interface (Recommended)

```bash
# Start the application
python app.py
uvicorn app.main:app --reload
```

The web interface will be available at `http://localhost:5000`

**Steps:**
1. Paste a TikTok video URL
2. Set maximum comments to scrape (1-10000)
3. Choose export format (JSON, CSV, Excel)
4. Click "Start Scraping"
5. Download the results when complete

### Command Line

```python
# Create a simple script
import asyncio
from scraper import TikTokCommentScraper

async def main():
    scraper = TikTokCommentScraper(headless=True)
    comments, metadata = await scraper.scrape_comments(
        video_url="https://www.tiktok.com/@username/video/123456789",
        max_comments=200
    )
    print(f"Scraped {len(comments)} comments")

asyncio.run(main())
```

## Project Structure

```
tiktok-scrape/
├── app.py                 # Flask web application
├── scraper.py            # Core scraping logic
├── exporter.py           # Data export functionality
├── config.py             # Configuration management
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables (optional)
├── templates/
│   └── index.html        # Web UI
├── exports/              # Exported files directory
├── logs/                 # Log files directory
└── venv/                 # Virtual environment
```

## API Endpoints

### POST /api/scrape
Scrapes comments from a TikTok video.

**Request:**
```json
{
  "video_url": "https://www.tiktok.com/@username/video/123456789",
  "max_comments": 200,
  "export_format": "json"
}
```

**Response:**
```json
{
  "success": true,
  "metadata": {
    "source_url": "...",
    "scrape_timestamp": "2024-01-01T12:00:00",
    "status": "success",
    "total_comments": 200,
    "errors": []
  },
  "summary": {
    "total_comments": 200,
    "total_likes": 5000,
    "total_replies": 150,
    "avg_likes": 25.0,
    "avg_replies": 0.75,
    "verified_users": 15
  },
  "export_file": "comments_20240101_120000.json"
}
```

### GET /api/status
Returns current scraping status.

### GET /api/exports
Lists all exported files.

**Response:**
```json
{
  "files": [
    {
      "name": "comments_20240101_120000.json",
      "size": 102400,
      "modified": "2024-01-01T12:00:00"
    }
  ]
}
```

### GET /api/download/<filename>
Downloads an exported file.

### POST /api/validate-url
Validates a TikTok URL and extracts video ID.

**Request:**
```json
{
  "url": "https://www.tiktok.com/@username/video/123456789"
}
```

## Data Export

### JSON
- Preserves all data structure
- Human-readable format
- Easy to parse in any language

### CSV
- Compatible with Excel and spreadsheets
- Column headers match data fields
- Suitable for bulk analysis

### Excel
- Auto-formatted columns
- Professional appearance
- Easy data visualization
- Recommended for presentations

## Error Handling

The scraper includes:
- ✓ Automatic retries (3 attempts by default)
- ✓ URL validation
- ✓ Exception handling
- ✓ Detailed error logging
- ✓ User-friendly error messages

## Logging

Logs are saved to `logs/` directory:
- `scraper.log` - Scraping operations
- `app.log` - Web application operations

View logs in real-time:
```bash
tail -f logs/scraper.log
```

## Performance Notes

- Single video: ~30-60 seconds (depending on network/TikTok rate limits)
- Headless mode: Faster but may bypass some security checks
- Visible mode: Slower but handles CAPTCHAs manually if needed
- Rate limiting: Respects TikTok's rate limits automatically

## Troubleshooting

### Issue: "Invalid TikTok URL"
- Ensure URL is from `tiktok.com`
- Include the complete video URL
- Check for typos

### Issue: Scraper hangs
- Try with fewer comments (max_comments=100)
- Check internet connection
- Restart the application

### Issue: CAPTCHA prompt
- Set `headless=False` in config to see and solve manually
- Wait for a few minutes and retry
- Consider using proxies

### Issue: "Connection refused"
- Ensure Flask app is running (`python app.py`)
- Check if port 5000 is available
- Try a different port: `PORT=8000 python app.py`

## Rate Limiting

TikTok implements rate limiting. To avoid being blocked:
- Don't scrape too many videos in rapid succession
- Use reasonable max_comments values
- Add delays between requests if needed
- Consider using proxies for large-scale operations

## Privacy & Terms of Service

- Respect TikTok's Terms of Service
- Don't scrape for unauthorized commercial use
- Respect user privacy
- Follow local data protection laws

## License

This project is provided as-is for educational and authorized scraping purposes.

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review logs in `logs/` directory
3. Ensure all dependencies are installed correctly
4. Verify TikTok URL is valid

## Future Enhancements

- [ ] Batch video scraping
- [ ] Advanced filtering options
- [ ] Sentiment analysis
- [ ] Comment categorization
- [ ] Database storage (MongoDB/PostgreSQL)
- [ ] REST API with authentication
- [ ] Scheduled scraping jobs
