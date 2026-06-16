# TikTok Scraper - Edge Cases & URL Support

This document details all supported URL types and edge cases for the TikTok scraper.

## Supported URL Types

### 1. Long-Form Video URLs
Standard TikTok video URLs with creator handle and video ID.

```
https://www.tiktok.com/@username/video/7647141380745121044
```

**Features:**
- 19-digit video ID in URL
- Includes creator handle (`@username`)
- Used for regular short videos
- 100% supported ✅

**Example:**
```bash
curl -X POST http://localhost:5000/api/scrape \
  -H "Content-Type: application/json" \
  -d '{
    "video_url": "https://www.tiktok.com/@tiktok/video/7647141380745121044",
    "max_comments": 200,
    "include_replies": false
  }'
```

### 2. Photo/Carousel URLs (NEW!)
TikTok photo posts and photo carousels (collections of images).

```
https://www.tiktok.com/@sewaro_accessorie/photo/7651936923140820242
```

**Features:**
- 19-digit post ID in URL
- Same creator handle format as videos
- Comments supported ✅
- **Status:** Now supported via library monkey-patch!
- Works like videos from an API perspective
- **NEW:** Monkey-patched TikTokApi to accept `/photo/` URLs

**Technical Details:**
- TikTokApi v7.3.3 only accepted `/video/` URLs
- We monkey-patch `helpers.extract_video_id_from_url()` at runtime
- Now accepts both `/video/` and `/photo/` URL formats
- See scraper.py for implementation

**Example:**
```bash
curl -X POST http://localhost:5000/api/scrape \
  -H "Content-Type: application/json" \
  -d '{
    "video_url": "https://www.tiktok.com/@sewaro_accessorie/photo/7651936923140820242",
    "max_comments": 200
  }'
```

### 3. Short Links (vm.tiktok.com)
Shortened TikTok URLs used for sharing (mobile).

```
https://vm.tiktok.com/ZGeVwXy1/
https://vt.tiktok.com/ZGeVwXy1/
https://v.tiktok.com/ZGeVwXy1/
```

**Features:**
- Alphanumeric ID (variable length)
- Requires resolution to determine post type
- Supported ✅
- Post type will show as "unknown" until fetched

**Example:**
```bash
curl -X POST http://localhost:5000/api/scrape \
  -H "Content-Type: application/json" \
  -d '{
    "video_url": "https://vm.tiktok.com/ZGeVwXy1/",
    "max_comments": 200
  }'
```

---

## API Request/Response Examples

### Basic Request (Video)
```json
{
  "video_url": "https://www.tiktok.com/@tiktok/video/7647141380745121044",
  "max_comments": 200,
  "export_format": "json"
}
```

**Response:**
```json
{
  "success": true,
  "metadata": {
    "source_url": "https://www.tiktok.com/@tiktok/video/7647141380745121044",
    "post_id": "7647141380745121044",
    "post_type": "video",
    "scrape_timestamp": "2026-06-11T15:30:00.123456",
    "status": "success",
    "total_comments": 200,
    "total_replies": 0,
    "include_replies": false,
    "errors": []
  },
  "summary": {
    "total_comments": 200,
    "total_likes": 15234,
    "total_replies": 342,
    "avg_likes": 76.17,
    "avg_replies": 1.71,
    "verified_users": 12
  },
  "export_file": "7647141380745121044.json",
  "total_comments": 200
}
```

### Advanced Request (With Replies)
```json
{
  "video_url": "https://www.tiktok.com/@sewaro_accessorie/photo/7651936923140820242",
  "max_comments": 50,
  "export_format": "json",
  "include_replies": true
}
```

**Response:** Same as above, but comments will include `replies_list`:

```json
{
  "id": "1234567890",
  "username": "john_doe",
  "text": "Great content!",
  "likes": 42,
  "replies": 3,
  "created_at": "2026-06-10T12:30:00",
  "is_reply": false,
  "replies_list": [
    {
      "id": "1234567891",
      "username": "jane_smith",
      "text": "Thanks so much! 😊",
      "likes": 5,
      "is_reply": true,
      "parent_comment_id": "1234567890"
    }
  ]
}
```

---

## Comment Data Fields

### Standard Fields (All Comments)
```python
{
    "id": "1234567890",                           # Comment ID
    "username": "john_doe",                       # Creator username
    "nickname": "John Doe",                       # Display name
    "user_id": "123456789",                       # User ID
    "avatar_url": "https://...",                  # Profile picture URL
    "text": "Great video!",                       # Comment text
    "likes": 42,                                  # Likes on comment
    "replies": 3,                                 # Number of replies
    "created_at": "2026-06-10T12:30:00",         # ISO timestamp
    "user_verified": false,                       # Creator verified badge
    "user_follower_count": 50000,                # Creator followers
    "has_sticker": false,                         # Comment has sticker
    "sticker_id": null,                           # Sticker ID if present
    "is_reply": false                             # Is this a reply? (new)
}
```

### Reply-Specific Fields
```python
{
    ...                                           # All standard fields
    "is_reply": true,                             # Marked as reply
    "parent_comment_id": "1234567890",           # Parent comment ID
    "replies_list": []                            # (empty, replies don't nest further)
}
```

---

## Edge Cases & Limitations

### 1. **Comments on Private Accounts**
- ❌ Cannot scrape (account is private)
- Error: `EmptyResponseException` or `Page blocked by TikTok`
- Solution: Use a logged-in session token (MS_TOKEN)

### 2. **Deleted Posts/Comments**
- ✅ Returns empty comment list
- Status: `success` with `total_comments: 0`
- No error thrown

### 3. **Comments Disabled**
- ✅ Returns empty list
- Metadata shows `total_comments: 0`
- No error

### 4. **Very Old Posts**
- ⚠️ May have pagination issues
- Comments beyond 1000 may not be accessible
- TikTok limitation, not scraper limitation

### 5. **Bot Detection**
- Strategy rotation handles this automatically
- Tries: headless chromium → visible chromium → firefox
- Use MS_TOKEN cookie for reliability
- See [TikTok bot-detection setup](../memory/tiktok-bot-detection-setup.md)

### 6. **Rate Limiting**
- TikTok may block after many rapid requests
- Scraper includes exponential backoff
- Solution: Spread requests over time or use proxy

### 7. **International Characters**
- ✅ Fully supported (UTF-8)
- Handles emojis in comments
- All character encodings preserved

### 8. **Very Long Comments**
- ✅ Supported (no truncation)
- Text stored as-is
- Full text available in exports

### 9. **Media in Comments**
- ⚠️ Stickers detected but not downloaded
- `has_sticker: true` if comment has sticker
- `sticker_id` available for reference
- Image/video references in text only (links)

### 10. **Hashtags & Mentions**
- ✅ Preserved in comment text
- Formatted as `#hashtag` and `@username`
- Not parsed separately

---

## New Features (This Session)

### ✅ Photo URL Recognition
```python
s.validate_url("https://www.tiktok.com/@sewaro_accessorie/photo/7651936923140820242")
# Returns: True

s.get_post_type("https://www.tiktok.com/@sewaro_accessorie/photo/7651936923140820242")
# Returns: "photo"
```

**Limitation:** While photo URLs are recognized, the TikTokApi library doesn't support scraping from them yet. This is a library limitation, not our scraper.

### ✅ Comment Replies (Beta)
Now you can fetch replies to top-level comments:

```bash
curl -X POST http://localhost:5000/api/scrape \
  -H "Content-Type: application/json" \
  -d '{
    "video_url": "https://www.tiktok.com/@tiktok/video/7647141380745121044",
    "max_comments": 50,
    "include_replies": true
  }'
```

**Features:**
- Fetches up to 10 replies per comment
- Marks replies with `"is_reply": true`
- Includes `parent_comment_id` for tracking
- ⚠️ Significantly slower (multi-level fetching)

**Performance:**
- Without replies: 10-20 seconds
- With replies: 3-5 minutes

### ✅ Enhanced Comment Data
Each comment now includes:
- `user_id` - Creator's unique ID
- `user_follower_count` - Creator's follower count
- `has_sticker` - Whether comment has sticker
- `sticker_id` - Sticker reference ID (if present)
- `is_reply` - Boolean indicating if it's a reply
- `parent_comment_id` - ID of parent (for replies only)

---

## Filtering & Advanced Features

### Available Filters
```python
filters = {
    "min_likes": 10,          # Comments with at least 10 likes
    "min_replies": 2,         # Comments with at least 2 replies
    "verified_only": True     # Only from verified creators
}
```

**Usage:**
```bash
curl -X POST http://localhost:5000/api/scrape \
  -H "Content-Type: application/json" \
  -d '{
    "video_url": "https://www.tiktok.com/@tiktok/video/7647141380745121044",
    "max_comments": 200,
    "filters": {
      "min_likes": 5,
      "verified_only": false
    }
  }'
```

### Include Replies (NEW)
```bash
curl -X POST http://localhost:5000/api/scrape \
  -H "Content-Type: application/json" \
  -d '{
    "video_url": "https://www.tiktok.com/@tiktok/video/7647141380745121044",
    "max_comments": 50,
    "include_replies": true
  }'
```

- ⚠️ Significantly slower (fetches nested data)
- Only first 10 replies per comment
- Consider using `max_comments=50` to keep runtime reasonable

---

## URL Validation

### Valid URLs (Examples)
```
✅ https://www.tiktok.com/@username/video/7647141380745121044
✅ https://www.tiktok.com/@username/photo/7651936923140820242
✅ https://vm.tiktok.com/ZGeVwXy1/
✅ https://vt.tiktok.com/ZGeVwXy1/
✅ https://v.tiktok.com/ZGeVwXy1/
```

### Invalid or Unsupported URLs (Examples)
```
❌ https://www.tiktok.com/@username  (no post ID)
❌ https://www.tiktok.com/discover   (not a post)
❌ https://www.tiktok.com/@username/live/123  (livestream, not supported)
❌ https://www.tiktok.com/search     (search page)
```

**About Photo URLs:**
Photo URLs are **now fully supported** thanks to a runtime monkey-patch! The TikTokApi library (v7.3.3) originally only accepted `/video/` URLs. We patched the `extract_video_id_from_url()` function to also accept `/photo/` URLs.

✅ You can now scrape comments from photo posts just like videos!

### Check URL Validity via API
```bash
curl -X POST http://localhost:5000/api/validate-url \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.tiktok.com/@tiktok/video/7647141380745121044"
  }'
```

**Response:**
```json
{
  "valid": true,
  "video_id": "7647141380745121044",
  "message": "Valid TikTok URL"
}
```

---

## Performance Characteristics

### Typical Timings
```
Headless chromium (fast):    10-20 seconds for 200 comments
Visible chromium (slower):   20-40 seconds for 200 comments
With replies (much slower):  3-5 minutes for 50 comments with replies
```

### Factors Affecting Speed
1. **Network speed** - Most critical
2. **Comment count** - Linear scaling
3. **Replies fetching** - ~30 extra seconds per comment with replies
4. **MS_TOKEN freshness** - Fresh tokens are faster
5. **Server load** - TikTok's server response times vary

### Optimization Tips
```python
# Fast scraping
{
    "max_comments": 50,
    "include_replies": False
}

# Balanced
{
    "max_comments": 100,
    "include_replies": False
}

# Comprehensive (slow)
{
    "max_comments": 200,
    "include_replies": True
}
```

---

## Export Formats

All formats support the full data structure:

### JSON
```bash
./start.sh logs | grep "Successfully scraped"
# Check exports/ folder
cat exports/7647141380745121044.json | jq '.[] | {username, text, likes}'
```

### CSV
```bash
# Includes headers
id,username,nickname,avatar_url,text,likes,replies,created_at,user_verified
123456,john_doe,John Doe,https://...,Great!,42,3,2026-06-10T12:30:00,False
```

### Excel (.xlsx)
- Same columns as CSV
- Open in Excel/Sheets
- Colors for headers
- Auto-width columns

---

## Troubleshooting

### "Invalid TikTok URL format"
**Solution:** Check URL format using `/api/validate-url` endpoint

### Empty comment list
1. Check if comments are disabled
2. Try with MS_TOKEN set in .env
3. Verify URL is correct
4. Check logs: `./start.sh logs`

### TimeoutError
**Solution:** Run with lower `max_comments` value:
```json
{ "max_comments": 50 }
```

### Bot detection (empty response)
**Solution:** See [bot-detection setup](../memory/tiktok-bot-detection-setup.md)

---

## References

- **URL Formats:** TikTok's official URL structure
- **Comment API:** TikTokApi 7.3.3 library
- **Filters:** Custom implemented
- **Replies:** Available in TikTokApi comment.replies() method
