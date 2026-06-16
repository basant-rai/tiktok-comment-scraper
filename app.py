from typing import Dict, Any
from fastapi.responses import JSONResponse
from fastapi import FastAPI, HTTPException
import asyncio
import logging
import os
import json
from datetime import datetime
from typing import Optional, Dict, Any
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import aiofiles
import re

from scraper import TikTokCommentScraper
from exporter import DataExporter
from config import Config

os.makedirs(Config.LOGS_DIR, exist_ok=True)
os.makedirs(Config.OUTPUT_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(f"{Config.LOGS_DIR}/app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="TikTok Comment Scraper API",
    description="Scrape and analyze comments from TikTok videos",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

scraper = TikTokCommentScraper(headless=True)
exporter = DataExporter(Config.OUTPUT_DIR)

templates_dir = os.path.join(os.path.dirname(__file__), "templates")

scraping_status = {
    "is_running": False,
    "progress": 0,
    "total": 0,
    "current_url": None,
    "error": None
}


class ScrapeRequest(BaseModel):
    video_url: str = Field(..., description="TikTok post URL (video, photo, or short link)")
    max_comments: int = Field(
        200, ge=1, le=10000, description="Maximum comments to scrape")
    export_format: str = Field(
        "json", description="Export format: json, csv, or excel")
    include_replies: bool = Field(
        False, description="Fetch replies to each comment")


class ValidateURLRequest(BaseModel):
    url: str = Field(..., description="TikTok URL to validate")


class FileInfo(BaseModel):
    name: str
    size: int
    modified: str


class ExportSummary(BaseModel):
    total_comments: int
    total_likes: int = 0
    total_replies: int = 0
    avg_likes: float = 0.0
    avg_replies: float = 0.0
    verified_users: int = 0


class ScrapeResponse(BaseModel):
    success: bool
    metadata: dict
    summary: ExportSummary
    export_file: str
    total_comments: int


@app.get("/", response_class=HTMLResponse)
async def root():
    try:
        html_path = os.path.join(templates_dir, "index.html")
        with open(html_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return """
        <html>
            <body>
                <h1>TikTok Comment Scraper</h1>
                <p>API running successfully!</p>
                <p><a href="/docs">API Documentation</a></p>
            </body>
        </html>
        """


def extract_tiktok_id(url):
    """Extract post ID from TikTok URL (video, photo, or short link)."""
    patterns = [
        r"(?:vm|vt|v)\.tiktok\.com/(\w+)",  # Short links
        r"tiktok\.com/@[\w.-]+/(?:video|photo)/(\d+)",  # Long links
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    return "ID not found in the URL"


@app.post("/api/scrape", response_model=ScrapeResponse)
async def api_scrape(request: ScrapeRequest):
    try:
        video_url = request.video_url.strip()
        max_comments = request.max_comments
        export_format = request.export_format

        if not video_url:
            raise HTTPException(
                status_code=400, detail="Video URL is required")

        if not scraper.validate_url(video_url):
            raise HTTPException(
                status_code=400, detail="Invalid TikTok URL format")

        if export_format not in Config.EXPORT_FORMATS:
            raise HTTPException(
                status_code=400,
                detail=f"Export format must be one of {Config.EXPORT_FORMATS}"
            )

        scraping_status["is_running"] = True
        scraping_status["current_url"] = video_url
        scraping_status["error"] = None

        try:
            comments, metadata = await scraper.scrape_comments(
                video_url, max_comments, include_replies=request.include_replies
            )
            video_id = extract_tiktok_id(request.video_url)

            if export_format == "json":
                export_path = exporter.to_json(comments, f"{video_id}.json")
            elif export_format == "csv":
                export_path = exporter.to_csv(comments, f"{video_id}.csv")
            elif export_format == "excel":
                export_path = exporter.to_excel(comments, f"{video_id}.xlsx")

            summary_data = exporter.get_export_summary(comments)
            summary = ExportSummary(**summary_data)

            scraping_status["is_running"] = False

            return ScrapeResponse(
                success=True,
                metadata=metadata,
                summary=summary,
                export_file=os.path.basename(export_path),
                total_comments=len(comments)
            )

        except Exception as e:
            scraping_status["is_running"] = False
            scraping_status["error"] = str(e)
            logger.error(f"Scraping error: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/status")
async def api_status():
    return scraping_status


@app.get("/api/exports")
async def api_list_exports():
    try:
        files = []
        if os.path.exists(Config.OUTPUT_DIR):
            for filename in sorted(os.listdir(Config.OUTPUT_DIR), reverse=True):
                filepath = os.path.join(Config.OUTPUT_DIR, filename)
                if os.path.isfile(filepath):
                    files.append(FileInfo(
                        name=filename,
                        size=os.path.getsize(filepath),
                        modified=datetime.fromtimestamp(
                            os.path.getmtime(filepath)).isoformat()
                    ))
        return {"files": files}
    except Exception as e:
        logger.error(f"Export list error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/download/{filename}")
async def api_download(filename: str):
    try:
        filepath = os.path.join(Config.OUTPUT_DIR, filename)

        if not os.path.exists(filepath):
            raise HTTPException(status_code=404, detail="File not found")

        if not os.path.isfile(filepath):
            raise HTTPException(status_code=400, detail="Invalid file path")

        return FileResponse(
            path=filepath,
            filename=filename,
            media_type="application/octet-stream"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Download error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/comments/{video_id}")
async def get_comments_from_file(video_id: str) -> Dict[str, Any]:
    """
    Check if comments file exists for this video_id.
    If yes, return the data. If no, return status indicating need to scrape.
    """
    try:
        # Construct the expected filename
        filename = f"{video_id}.json"
        filepath = os.path.join(Config.OUTPUT_DIR, filename)

        # Debug logging
        print(f"🔍 Checking for file: {filepath}")
        print(f"📁 OUTPUT_DIR: {Config.OUTPUT_DIR}")
        print(f"📄 File exists: {os.path.exists(filepath)}")

        # Check if file exists
        if os.path.exists(filepath) and os.path.isfile(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            return {
                "status": "found",
                "data": data,
                "filename": filename
            }
        else:
            # Return 200 with not_found status instead of throwing 404
            return {
                "status": "not_found",
                "message": "No cached comments found. Please scrape first.",
                "video_id": video_id
            }

    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error: {e}")
        raise HTTPException(
            status_code=500, detail="Invalid JSON format in file")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"Error reading file: {str(e)}")


@app.post("/api/validate-url")
async def api_validate_url(request: ValidateURLRequest):
    try:
        url = request.url.strip()

        is_valid = scraper.validate_url(url)
        post_id = scraper.extract_post_id(url) if is_valid else None
        post_type = scraper.get_post_type(url) if is_valid else None

        return {
            "valid": is_valid,
            "post_id": post_id,
            "post_type": post_type,
            "message": "Valid TikTok URL" if is_valid else "Invalid TikTok URL format"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return {
        "error": exc.detail,
        "status_code": exc.status_code
    }


if __name__ == "__main__":
    import uvicorn
    logger.info("Starting TikTok Comment Scraper with FastAPI")
    uvicorn.run(
        "app:app",
        host=Config.HOST,
        port=Config.PORT,
        reload=Config.DEBUG
    )
