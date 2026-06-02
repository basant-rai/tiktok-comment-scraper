# Deployment Guide

Complete guide for deploying TikTok Comment Scraper to various platforms.

## Local Deployment (Recommended for Development)

### Prerequisites
- Python 3.8+
- pip or poetry

### Steps

```bash
# 1. Clone/navigate to project
cd tiktok-scrape

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create directories
mkdir -p exports logs

# 5. Run the application
python app.py
```

Visit: `http://localhost:5000`

---

## Vercel Deployment (Cloud - Recommended)

### ⚠️ Important Limitations

**Vercel has a 60-second timeout limit for serverless functions.** This means:
- Large comment scrapes may timeout
- Best for scraping 50-200 comments per video
- For larger volumes, use local deployment

### Prerequisites
- Vercel account (free at vercel.com)
- GitHub account
- TikTok scraper repository

### Step 1: Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit: TikTok comment scraper"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/tiktok-scrape.git
git push -u origin main
```

### Step 2: Deploy to Vercel

**Option A: Via Vercel Dashboard (Easiest)**

1. Go to [vercel.com](https://vercel.com)
2. Click "New Project"
3. Select your GitHub repository
4. Framework: **Flask**
5. Click "Deploy"

**Option B: Via Vercel CLI**

```bash
npm install -g vercel
vercel login
vercel
```

### Step 3: Configuration

Vercel will automatically detect the Flask app. No additional configuration needed.

### Step 4: Set Environment Variables (Optional)

In Vercel Dashboard:
1. Go to Project Settings → Environment Variables
2. Add variables:
   ```
   DEBUG=False
   HOST=0.0.0.0
   PORT=3000
   HEADLESS=True
   ```

### Deployment Result

Your app will be live at: `https://your-project.vercel.app`

### Known Vercel Limitations

| Limitation | Impact | Workaround |
|-----------|--------|-----------|
| 60-second timeout | Large scrapes fail | Reduce max_comments to 50-200 |
| No persistent storage | Exports deleted after deployment | Download immediately after scraping |
| Browser instances | TikTokApi may not work | Works for basic scraping |
| Cold starts | First request is slow | Pre-warm with requests |

---

## Docker Deployment

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p exports logs

EXPOSE 5000

CMD ["python", "app.py"]
```

### Build & Run

```bash
docker build -t tiktok-scraper .
docker run -p 5000:5000 tiktok-scraper
```

---

## Heroku Deployment

### Prerequisites
- Heroku account (heroku.com)
- Heroku CLI installed

### Steps

```bash
# 1. Login to Heroku
heroku login

# 2. Create Heroku app
heroku create your-app-name

# 3. Deploy code
git push heroku main

# 4. View logs
heroku logs --tail
```

### Procfile (Required)

Create a `Procfile` in the root:

```
web: python app.py
```

### Issues on Heroku

- May require headless browser setup
- Free tier has 30-minute timeout limit
- Dynos sleep after 30 minutes of inactivity

---

## AWS Lambda Deployment

### Using AWS SAM

```bash
pip install aws-sam-cli
sam init
sam build
sam deploy --guided
```

### Limitations

- 15-minute timeout
- Memory-constrained
- Cold start latency
- Not ideal for browser automation

---

## DigitalOcean App Platform

### Steps

1. Connect GitHub repository
2. Choose Python as runtime
3. Set build command: `pip install -r requirements.txt`
4. Set run command: `python app.py`
5. Deploy

Supports persistent storage and longer timeouts (10 minutes).

---

## Self-Hosted (VPS)

### Prerequisites
- Linux VPS (Ubuntu 20.04+)
- SSH access
- Domain name (optional)

### Installation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3 python3-pip python3-venv -y

# Clone repository
git clone https://github.com/YOUR_USERNAME/tiktok-scrape.git
cd tiktok-scrape

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create directories
mkdir -p exports logs
```

### Using Gunicorn (Production)

```bash
pip install gunicorn

gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Using Nginx (Reverse Proxy)

```bash
sudo apt install nginx -y

sudo nano /etc/nginx/sites-available/default
```

Add:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Restart Nginx:
```bash
sudo systemctl restart nginx
```

### Using Systemd (Auto-start)

Create `/etc/systemd/system/tiktok-scraper.service`:

```ini
[Unit]
Description=TikTok Comment Scraper
After=network.target

[Service]
Type=notify
User=ubuntu
WorkingDirectory=/home/ubuntu/tiktok-scrape
ExecStart=/home/ubuntu/tiktok-scrape/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable:
```bash
sudo systemctl enable tiktok-scraper
sudo systemctl start tiktok-scraper
```

---

## Performance Recommendations by Platform

| Platform | Max Comments | Timeout | Best For |
|----------|--------------|---------|----------|
| **Local** | Unlimited | None | Development, large volumes |
| **Vercel** | 50-200 | 60s | Quick demos, API |
| **Docker** | Unlimited | None | Containerized apps |
| **Heroku** | 100-500 | 30m | Small workloads |
| **VPS** | Unlimited | None | Production, high volume |

---

## Monitoring & Logging

### Local
```bash
tail -f logs/app.log
tail -f logs/scraper.log
```

### Vercel
```bash
vercel logs
```

### Heroku
```bash
heroku logs --tail
```

### Self-hosted
```bash
journalctl -u tiktok-scraper -f
```

---

## Troubleshooting Deployment

### "Module not found" Error
```bash
pip install -r requirements.txt --upgrade
```

### Timeout Issues
- Reduce `max_comments`
- Use local deployment for large volumes
- Upgrade hosting plan

### Browser Automation Fails
- Set `headless=True` in config
- May need Chromium installation
- Not guaranteed on all platforms

### Storage/Exports Not Persistent
- On serverless platforms, download immediately
- Use external storage (S3, Firebase)
- Or use persistent VPS

---

## Production Checklist

- [ ] Update `DEBUG=False` in config
- [ ] Set strong `SECRET_KEY` in Flask
- [ ] Configure logging properly
- [ ] Set up monitoring/alerts
- [ ] Enable HTTPS/SSL
- [ ] Rate limit API endpoints
- [ ] Add authentication if needed
- [ ] Regular backups of exports
- [ ] Monitor server resources
- [ ] Document deployment process

---

## Recommended Setup

**For Development:**
- Local deployment with `./start.sh`

**For Small Scale:**
- Vercel (60-second limits)
- Or Docker on any host

**For Production/Large Scale:**
- Self-hosted VPS with Gunicorn + Nginx
- Or Docker + Kubernetes
- With persistent storage and monitoring

---

## Support

Having deployment issues?
1. Check the logs in your deployment platform
2. Verify `requirements.txt` is up to date
3. Ensure Python version compatibility
4. Test locally first before deploying
5. Check platform-specific documentation
