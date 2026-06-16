import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from typing import List, Dict, Optional, AsyncIterator
from dotenv import load_dotenv
import re
import requests

load_dotenv()

# IMPORTANT: Monkey-patch BEFORE importing TikTokApi
# We need to patch at the sys.modules level before video.py is loaded

def _patched_extract_video_id(url, headers={}, proxy=None):
    """Extract post ID from TikTok URL (supports both video and photo)."""
    url = requests.head(url=url, allow_redirects=True, headers=headers, proxies=proxy).url

    if "@" in url and ("/video/" in url or "/photo/" in url):
        # Determine separator and extract ID
        sep = "/video/" if "/video/" in url else "/photo/"
        return url.split(sep)[1].split("?")[0]
    else:
        raise TypeError(
            "URL format not supported. Below is an example of a supported url.\n"
            "https://www.tiktok.com/@therock/video/6829267836783971589\n"
            "or\n"
            "https://www.tiktok.com/@therock/photo/6829267836783971589"
        )

# Patch at the module level BEFORE any imports
import TikTokApi.helpers
TikTokApi.helpers.extract_video_id_from_url = _patched_extract_video_id

# Patch in sys.modules in case it's cached
if 'TikTokApi.helpers' in sys.modules:
    sys.modules['TikTokApi.helpers'].extract_video_id_from_url = _patched_extract_video_id

from TikTokApi import TikTokApi

# ALSO patch the reference in video.py (it imported the function directly)
from TikTokApi.api import video
video.extract_video_id_from_url = _patched_extract_video_id

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

    def extract_post_id(self, url: str) -> Optional[str]:
        """Extract ID from TikTok URL (video, photo, or short link)."""
        patterns = [
            r"(?:vm|vt|v)\.tiktok\.com/(\w+)",  # Short links: vm.tiktok.com, vt.tiktok.com
            r"tiktok\.com/@[\w.-]+/(?:video|photo)/(\d+)",  # Long links: video/photo
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    def get_post_type(self, url: str) -> Optional[str]:
        """Determine if URL is a video, photo, or other content type."""
        if "/video/" in url:
            return "video"
        elif "/photo/" in url:
            return "photo"
        elif any(x in url for x in ["vm.tiktok.com", "vt.tiktok.com", "v.tiktok.com"]):
            return "unknown"  # Need to resolve to determine type
        return None

    def validate_url(self, url: str) -> bool:
        """Validate if URL is a valid TikTok post (video, photo, or short link)."""
        if "tiktok.com" not in url:
            return False

        # Accept video, photo, or short links
        valid_patterns = [
            "tiktok.com/@" in url and ("/video/" in url or "/photo/" in url),
            any(x in url for x in ["vm.tiktok.com", "vt.tiktok.com", "v.tiktok.com"])
        ]
        return any(valid_patterns)

    async def scrape_comments(
        self,
        video_url: str,
        max_comments: int = 200,
        filters: Optional[Dict] = None,
        include_replies: bool = False
    ) -> tuple[List[Dict], Dict]:
        """
        Scrape comments from a TikTok post (video or photo).

        Args:
            video_url: TikTok post URL (video, photo, or short link)
            max_comments: Maximum number of top-level comments to fetch
            filters: Optional filters (min_likes, min_replies, verified_only)
            include_replies: Whether to fetch replies to each comment

        Returns:
            Tuple of (comments list, metadata dict)
        """

        if not self.validate_url(video_url):
            raise ValueError(f"Invalid TikTok URL: {video_url}")

        post_type = self.get_post_type(video_url)
        post_id = self.extract_post_id(video_url)

        all_comments = []
        metadata = {
            "source_url": video_url,
            "post_id": post_id,
            "post_type": post_type,
            "scrape_timestamp": datetime.now().isoformat(),
            "status": "pending",
            "total_comments": 0,
            "total_replies": 0,
            "include_replies": include_replies,
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
                    self._scrape_once(video_url, max_comments, filters, strategy, include_replies),
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
        strategy: Dict,
        include_replies: bool = False
    ) -> List[Dict]:
        """Scrape comments (and optionally replies) from a TikTok post."""
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

            post = api.video(url=video_url)

            async for comment in post.comments(count=max_comments):
                try:
                    entry = self._parse_comment(comment.as_dict)

                    if self._apply_filters(entry, filters):
                        comments.append(entry)
                        logger.info(f"[{len(comments)}] @{entry['username']}: {entry['text'][:50]}")

                        # Optionally fetch replies to this comment
                        if include_replies and hasattr(comment, 'replies') and comment.reply_comment_total > 0:
                            try:
                                replies = await self._fetch_replies(comment, filters)
                                if replies:
                                    entry["replies_list"] = replies
                                    logger.info(f"  └─ Fetched {len(replies)} replies to this comment")
                            except Exception as e:
                                logger.warning(f"Failed to fetch replies for comment {entry['id']}: {e}")

                        if len(comments) >= max_comments:
                            break

                except Exception as e:
                    logger.warning(f"Error parsing comment: {e}")
                    continue

        return comments

    async def _fetch_replies(self, comment: Dict, filters: Optional[Dict], max_replies: int = 10) -> List[Dict]:
        """Fetch replies to a specific comment."""
        replies = []
        try:
            # TikTokApi provides replies through comment.replies() if available
            if hasattr(comment, 'replies'):
                reply_count = 0
                async for reply in comment.replies(count=max_replies):
                    try:
                        reply_entry = self._parse_comment(reply.as_dict)
                        # Mark as a reply
                        reply_entry["is_reply"] = True
                        reply_entry["parent_comment_id"] = comment.as_dict.get("cid", "unknown")

                        if self._apply_filters(reply_entry, filters):
                            replies.append(reply_entry)
                            reply_count += 1

                        if reply_count >= max_replies:
                            break
                    except Exception as e:
                        logger.warning(f"Error parsing reply: {e}")
                        continue
        except (AttributeError, Exception) as e:
            # Comment might not have replies method, continue gracefully
            logger.debug(f"Could not fetch replies: {e}")

        return replies

    def _parse_comment(self, data: Dict) -> Dict:
        """Parse and extract comment data with all available fields."""
        user_data = data.get("user", {})
        avatar_list = user_data.get("avatar_medium", {}).get("url_list", [])
        avatar_url = avatar_list[0] if avatar_list else None

        return {
            "id": data.get("cid", "unknown"),
            "username": user_data.get("unique_id", "unknown"),
            "nickname": user_data.get("nickname", ""),
            "user_id": user_data.get("id", "unknown"),
            "avatar_url": avatar_url,
            "text": data.get("text", ""),
            "likes": data.get("digg_count", 0),
            "replies": data.get("reply_comment_total", 0),
            "created_at": datetime.fromtimestamp(data.get("create_time", 0)).isoformat() if data.get("create_time") else None,
            "user_verified": user_data.get("verify_info", {}).get("verify_detail", "") == "verified",
            "user_follower_count": user_data.get("follower_count"),
            "has_sticker": data.get("has_sticker", False),
            "sticker_id": data.get("sticker", {}).get("sticker_id") if data.get("sticker") else None,
            "is_reply": False,  # Default, will be set to True for actual replies
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
