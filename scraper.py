import asyncio
import json
import logging
import os
from datetime import datetime
from typing import List, Dict, Optional, AsyncIterator
from TikTokApi import TikTokApi
from dotenv import load_dotenv
import re

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/scraper.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class TikTokCommentScraper:
    def __init__(self, headless=True, max_retries=3, ms_token=None, attempt_timeout=180):
        self.headless = headless
        self.max_retries = max_retries
        self.session_count = 1
        self.ms_token = ms_token or os.getenv("MS_TOKEN") or None
        self.attempt_timeout = attempt_timeout

    def _session_strategies(self) -> List[Dict]:
        strategies = [{"browser": "chromium", "headless": True}]
        # A visible browser window is the hardest to detect, but needs a display
        if os.name == "nt" or os.environ.get("DISPLAY"):
            strategies.append({"browser": "chromium", "headless": False})
        strategies.append({"browser": "firefox", "headless": True})
        return strategies

    def extract_video_id(self, url: str) -> Optional[str]:
        patterns = [
            r"(?:vm|vt|v)\.tiktok\.com/(\w+)",
            r"tiktok\.com/@[\w.-]+/video/(\d+)"
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1) if pattern.endswith(r"(\w+)") else match.group(1)
        return None

    def validate_url(self, url: str) -> bool:
        return "tiktok.com" in url and ("video" in url or "vm.tiktok" in url or "vt.tiktok" in url)

    async def scrape_comments(
        self,
        video_url: str,
        max_comments: int = 200,
        filters: Optional[Dict] = None
    ) -> tuple[List[Dict], Dict]:

        if not self.validate_url(video_url):
            raise ValueError(f"Invalid TikTok URL: {video_url}")

        all_comments = []
        metadata = {
            "source_url": video_url,
            "scrape_timestamp": datetime.now().isoformat(),
            "status": "pending",
            "total_comments": 0,
            "errors": [],
        }

        strategies = self._session_strategies()

        for attempt in range(self.max_retries):
            strategy = strategies[attempt % len(strategies)]
            try:
                logger.info(
                    f"Attempt {attempt + 1}/{self.max_retries}: Scraping {video_url} "
                    f"(browser={strategy['browser']}, headless={strategy['headless']}, "
                    f"ms_token={'set' if self.ms_token else 'not set'})"
                )

                # Hard cap per attempt: a crashed/hung browser must not stall the retry loop
                all_comments = await asyncio.wait_for(
                    self._scrape_once(video_url, max_comments, filters, strategy),
                    timeout=self.attempt_timeout,
                )

                metadata["status"] = "success"
                metadata["total_comments"] = len(all_comments)
                logger.info(f"Successfully scraped {len(all_comments)} comments")
                return all_comments, metadata

            except Exception as e:
                error_msg = f"Attempt {attempt + 1} failed: {str(e) or type(e).__name__}"
                logger.error(error_msg)
                metadata["errors"].append(error_msg)

                if attempt < self.max_retries - 1:
                    wait_time = (attempt + 1) * 5
                    logger.info(f"Retrying in {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
                continue

        metadata["status"] = "failed"
        logger.error(f"Failed to scrape comments after {self.max_retries} attempts")
        return all_comments, metadata

    async def _scrape_once(
        self,
        video_url: str,
        max_comments: int,
        filters: Optional[Dict],
        strategy: Dict
    ) -> List[Dict]:
        comments = []

        async with TikTokApi() as api:
            await api.create_sessions(
                num_sessions=self.session_count,
                sleep_after=3,
                ms_tokens=[self.ms_token] if self.ms_token else None,
                browser=strategy["browser"],
                headless=strategy["headless"],
                suppress_resource_load_types=["image", "media", "font"],
            )

            video = api.video(url=video_url)

            async for comment in video.comments(count=max_comments):
                try:
                    entry = self._parse_comment(comment.as_dict)

                    if self._apply_filters(entry, filters):
                        comments.append(entry)
                        logger.info(f"[{len(comments)}] @{entry['username']}: {entry['text'][:50]}")

                        if len(comments) >= max_comments:
                            break

                except Exception as e:
                    logger.warning(f"Error parsing comment: {e}")
                    continue

        return comments

    def _parse_comment(self, data: Dict) -> Dict:
        return {
            "id": data.get("cid", "unknown"),
            "username": data.get("user", {}).get("unique_id", "unknown"),
            "nickname": data.get("user", {}).get("nickname", ""),
            "avatar_url": data.get("user", {}).get("avatar_medium", {}).get("url_list", [None])[0],
            "text": data.get("text", ""),
            "likes": data.get("digg_count", 0),
            "replies": data.get("reply_comment_total", 0),
            "created_at": datetime.fromtimestamp(data.get("create_time", 0)).isoformat(),
            "user_verified": data.get("user", {}).get("verify_info", {}).get("verify_detail", "") == "verified",
        }

    def _apply_filters(self, comment: Dict, filters: Optional[Dict]) -> bool:
        if not filters:
            return True

        if "min_likes" in filters and comment["likes"] < filters["min_likes"]:
            return False
        if "min_replies" in filters and comment["replies"] < filters["min_replies"]:
            return False
        if "verified_only" in filters and filters["verified_only"] and not comment["user_verified"]:
            return False

        return True


async def scrape_with_progress(url: str, max_comments: int = 200, filters: Optional[Dict] = None):
    scraper = TikTokCommentScraper(headless=True)
    comments, metadata = await scraper.scrape_comments(url, max_comments, filters)
    return comments, metadata
