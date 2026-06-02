import asyncio
import json
from TikTokApi import TikTokApi


async def scrape_comments(video_url, max_comments=200):
    all_comments = []

    async with TikTokApi() as api:
        await api.create_sessions(
            num_sessions=1,
            sleep_after=3,
            headless=False  # keep visible — may need to solve captcha manually
        )

        try:
            video = api.video(url="https://www.tiktok.com/@sreesti.chemjong/video/7645574045760539922")
            count = 0

            print(f"Fetching comments from: {video_url}\n")

            async for comment in video.comments(count=max_comments):
                data = comment.as_dict

                entry = {
                    "username": data.get("user", {}).get("unique_id", "unknown"),
                    "nickname": data.get("user", {}).get("nickname", ""),
                    "text": data.get("text", ""),
                    "likes": data.get("digg_count", 0),
                    "replies": data.get("reply_comment_total", 0),
                    "created_at": data.get("create_time", ""),
                }

                all_comments.append(entry)
                count += 1
                print(f"[{count}] @{entry['username']}: {entry['text'][:60]}")

        except Exception as e:
            print(f"Error: {e}")

    return all_comments


if __name__ == "__main__":
    VIDEO_URL = "https://www.tiktok.com/@sreesti.chemjong/video/7645574045760539922"

    results = asyncio.run(scrape_comments(VIDEO_URL, max_comments=200))

    print(f"\nTotal collected: {len(results)}")

    with open("comments.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print("Saved to comments.json")
