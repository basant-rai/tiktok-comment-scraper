import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DEBUG = os.getenv("DEBUG", "False") == "True"
    HOST = os.getenv("HOST", "127.0.0.1")
    PORT = int(os.getenv("PORT", 5000))

    SCRAPER_CONFIG = {
        "max_comments": 500,
        "timeout": 60,
        "retries": 3,
        "headless": True,
        "sleep_after": 2,
    }

    EXPORT_FORMATS = ["json", "csv", "excel"]
    OUTPUT_DIR = os.getenv("OUTPUT_DIR", "exports")
    LOGS_DIR = os.getenv("LOGS_DIR", "logs")

    MAX_VIDEOS_BATCH = 10
    REQUEST_TIMEOUT = 30
