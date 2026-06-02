# TikTok Comment Scraper - API Documentation

Complete API reference for the TikTok Comment Scraper.

## Base URL

```
http://localhost:5000
```

## Endpoints

### 1. Scrape Comments

**POST** `/api/scrape`

Scrapes comments from a TikTok video and exports them.

#### Request

```json
{
  "video_url": "https://www.tiktok.com/@username/video/7123456789",
  "max_comments": 200,
  "export_format": "json"
}
```

**Parameters:**
- `video_url` (string, required): Valid TikTok video URL
- `max_comments` (integer, optional): Max comments to scrape (1-10000, default: 200)
- `export_format` (string, required): Format to export - `json`, `csv`, or `excel`

#### Response (Success)

**Status:** `200 OK`

```json
{
  "success": true,
  "metadata": {
    "source_url": "https://www.tiktok.com/@username/video/7123456789",
    "scrape_timestamp": "2024-01-15T14:30:45.123456",
    "status": "success",
    "total_comments": 150,
    "errors": []
  },
  "summary": {
    "total_comments": 150,
    "total_likes": 3245,
    "total_replies": 89,
    "avg_likes": 21.63,
    "avg_replies": 0.59,
    "verified_users": 12
  },
  "export_file": "comments_20240115_143045.json",
  "total_comments": 150
}
```

#### Response (Error)

**Status:** `400 Bad Request` / `500 Internal Server Error`

```json
{
  "error": "Invalid TikTok URL format"
}
```

#### Example Usage

**cURL:**
```bash
curl -X POST http://localhost:5000/api/scrape \
  -H "Content-Type: application/json" \
  -d '{
    "video_url": "https://www.tiktok.com/@username/video/7123456789",
    "max_comments": 200,
    "export_format": "json"
  }'
```

**Python:**
```python
import requests

url = "http://localhost:5000/api/scrape"
data = {
    "video_url": "https://www.tiktok.com/@username/video/7123456789",
    "max_comments": 200,
    "export_format": "json"
}

response = requests.post(url, json=data)
result = response.json()
print(f"Scraped {result['total_comments']} comments")
```

**JavaScript:**
```javascript
const response = await fetch("http://localhost:5000/api/scrape", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    video_url: "https://www.tiktok.com/@username/video/7123456789",
    max_comments: 200,
    export_format: "json"
  })
});

const data = await response.json();
console.log(`Scraped ${data.total_comments} comments`);
```

---

### 2. Get Scraping Status

**GET** `/api/status`

Returns the current scraping status.

#### Response

```json
{
  "is_running": false,
  "progress": 0,
  "total": 0,
  "current_url": null,
  "error": null
}
```

#### Example Usage

```bash
curl http://localhost:5000/api/status
```

---

### 3. List Exported Files

**GET** `/api/exports`

Lists all exported comment files.

#### Response

```json
{
  "files": [
    {
      "name": "comments_20240115_143045.json",
      "size": 102400,
      "modified": "2024-01-15T14:30:45"
    },
    {
      "name": "comments_20240115_120000.csv",
      "size": 51200,
      "modified": "2024-01-15T12:00:00"
    }
  ]
}
```

#### Example Usage

```bash
curl http://localhost:5000/api/exports
```

---

### 4. Download Exported File

**GET** `/api/download/<filename>`

Downloads a previously exported file.

#### Parameters

- `filename` (string, URL path): Name of the file to download

#### Response

Binary file download with appropriate MIME type.

#### Example Usage

```bash
curl -O http://localhost:5000/api/download/comments_20240115_143045.json
```

**Browser:**
```
http://localhost:5000/api/download/comments_20240115_143045.json
```

---

### 5. Validate TikTok URL

**POST** `/api/validate-url`

Validates a TikTok URL and extracts the video ID.

#### Request

```json
{
  "url": "https://www.tiktok.com/@username/video/7123456789"
}
```

#### Response

```json
{
  "valid": true,
  "video_id": "7123456789",
  "message": "Valid TikTok URL"
}
```

#### Example Usage

**cURL:**
```bash
curl -X POST http://localhost:5000/api/validate-url \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.tiktok.com/@username/video/7123456789"}'
```

**JavaScript:**
```javascript
const response = await fetch("http://localhost:5000/api/validate-url", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    url: "https://www.tiktok.com/@username/video/7123456789"
  })
});

const data = await response.json();
console.log(data.valid ? "Valid URL" : "Invalid URL");
```

---

## Data Structure

### Comment Object

Each comment in the export contains:

```json
{
  "id": "7123456789000000001",
  "username": "john_doe",
  "nickname": "John Doe",
  "avatar_url": "https://...",
  "text": "Great video!",
  "likes": 45,
  "replies": 2,
  "created_at": "2024-01-15T10:30:00",
  "user_verified": true
}
```

**Fields:**
- `id` (string): Unique comment ID
- `username` (string): Creator's TikTok username
- `nickname` (string): Display name
- `avatar_url` (string): Profile picture URL
- `text` (string): Comment content
- `likes` (integer): Number of likes
- `replies` (integer): Number of replies to this comment
- `created_at` (string): ISO 8601 timestamp
- `user_verified` (boolean): Whether creator is verified

---

## Export Formats

### JSON
```json
[
  {
    "id": "...",
    "username": "...",
    ...
  }
]
```

### CSV
```
id,username,nickname,avatar_url,text,likes,replies,created_at,user_verified
7123456789000000001,john_doe,John Doe,https://...,Great video!,45,2,2024-01-15T10:30:00,true
```

### Excel (XLSX)
- Columns automatically formatted
- Widths adjusted for readability
- Single sheet named "Comments"

---

## Error Handling

### Common Error Codes

| Code | Message | Solution |
|------|---------|----------|
| 400 | Invalid TikTok URL format | Check URL format, use full video URL |
| 400 | Max comments must be between 1 and 10000 | Adjust max_comments value |
| 400 | Video URL is required | Provide a valid video URL |
| 404 | File not found | Check filename in exports list |
| 500 | Internal server error | Check logs, try again |

### Error Response Format

```json
{
  "error": "Invalid TikTok URL format"
}
```

---

## Rate Limiting & Best Practices

1. **Respect TikTok's Rate Limits**
   - Don't scrape more than a few videos per minute
   - TikTok may rate limit aggressive scraping

2. **Batch Requests**
   - Space out API calls by 5-10 seconds
   - Use reasonable max_comments values (100-500)

3. **Error Handling**
   - Implement retries with exponential backoff
   - Check HTTP status codes
   - Log failed requests

4. **Resource Management**
   - Monitor disk space in `exports/` directory
   - Periodically clean old export files
   - Use appropriate max_comments for your needs

---

## Example Workflow

```python
import requests
import time

BASE_URL = "http://localhost:5000"

# Step 1: Validate URL
video_url = "https://www.tiktok.com/@username/video/7123456789"

validate_response = requests.post(
    f"{BASE_URL}/api/validate-url",
    json={"url": video_url}
)

if not validate_response.json()["valid"]:
    print("Invalid URL!")
    exit(1)

# Step 2: Start scraping
scrape_response = requests.post(
    f"{BASE_URL}/api/scrape",
    json={
        "video_url": video_url,
        "max_comments": 200,
        "export_format": "json"
    }
)

result = scrape_response.json()

if result["success"]:
    print(f"✅ Scraped {result['total_comments']} comments")
    print(f"📊 Summary: {result['summary']}")
    
    # Step 3: Download file
    export_file = result["export_file"]
    download_response = requests.get(
        f"{BASE_URL}/api/download/{export_file}"
    )
    
    with open(export_file, "wb") as f:
        f.write(download_response.content)
    
    print(f"💾 Downloaded to {export_file}")
else:
    print(f"❌ Error: {result.get('error')}")
```

---

## Tips & Tricks

### Get Real-Time Status
```python
while True:
    status = requests.get(f"{BASE_URL}/api/status").json()
    if status["is_running"]:
        print(f"Scraping... {status['progress']}/{status['total']}")
    else:
        break
    time.sleep(1)
```

### Batch Scrape Multiple Videos
```python
videos = [
    "https://www.tiktok.com/@user1/video/123",
    "https://www.tiktok.com/@user2/video/456",
]

for video_url in videos:
    response = requests.post(
        f"{BASE_URL}/api/scrape",
        json={"video_url": video_url, "max_comments": 100, "export_format": "json"}
    )
    print(f"✅ {video_url}: {response.json()['total_comments']} comments")
    time.sleep(10)  # Rate limit
```

---

## Support

For API issues:
1. Check the logs: `tail -f logs/app.log`
2. Verify the server is running: `curl http://localhost:5000`
3. Test with the web interface first
4. Review this documentation for endpoint details
