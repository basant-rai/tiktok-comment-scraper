# Deployment Guide

This guide covers deploying the TikTok Scraper application to development and production environments using Docker and GitHub Actions.

## Quick Start

### Local Development
```bash
# Start with Docker (hot reload)
./start.sh dev

# Or start with local Python venv (legacy)
./start.sh local
```

Access the API at `http://localhost:5000`

### Production (Docker)
```bash
# Ensure .env has MS_TOKEN set
echo "MS_TOKEN=your_token_here" >> .env

# Start production containers
./start.sh prod

# View logs
./start.sh logs

# Stop
./start.sh stop
```

---

## Detailed Deployment

### Prerequisites

**For Docker deployment:**
- Docker >= 20.10
- Docker Compose >= 2.0
- Linux/macOS/WSL2 (Windows)

**For local Python deployment:**
- Python 3.11+
- pip
- Virtual environment support

### Environment Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/tiktok-scraper.git
   cd tiktok-scraper
   ```

2. **Create `.env` file:**
   ```bash
   cp .env.example .env
   # Edit .env and add your MS_TOKEN
   nano .env
   ```

3. **For production, set required variables:**
   ```env
   DEBUG=False
   HOST=0.0.0.0
   PORT=5000
   MS_TOKEN=your_actual_tiktok_token
   HEADLESS=True
   MAX_COMMENTS=500
   TIMEOUT=60
   RETRIES=3
   ```

---

## Docker Deployment Options

### Option 1: Development (Local with Hot Reload)

```bash
# Start
./start.sh dev

# In another terminal, view logs
./start.sh logs

# Stop when done
./start.sh stop
```

**Features:**
- Hot reload on file changes
- Debug mode enabled
- Faster iteration
- Source code mounted

---

### Option 2: Production (Optimized & Persistent)

```bash
# Build image
./start.sh build

# Start
./start.sh prod

# View logs
./start.sh logs

# Stop
./start.sh stop
```

**Features:**
- 2 uvicorn workers
- Health checks every 30s
- Persistent volumes
- Restart on failure
- No hot reload

---

### Option 3: Manual Docker Commands

```bash
# Development
docker-compose up
docker-compose logs -f
docker-compose down

# Production
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d
docker-compose -f docker-compose.prod.yml logs -f
docker-compose -f docker-compose.prod.yml down
```

---

## GitHub Actions Deployment

### Setting Up CI/CD

1. **Push repository to GitHub** (if not already done)
   ```bash
   git remote add origin https://github.com/yourusername/tiktok-scraper.git
   git push -u origin main
   ```

2. **Add secrets to GitHub:**
   - Go to Settings → Secrets and variables → Actions
   - Add `MS_TOKEN` (your TikTok token)
   - Add `SLACK_WEBHOOK_URL` (optional, for notifications)

3. **Workflows are automatically active:**
   - Code quality checks run on all PRs
   - Dev deployment runs on push to `scrape` branch
   - Production deployment runs on push to `main` or version tags

### Deployment Workflow

**Development Flow:**
```
feature-branch → PR to scrape
  ↓
  (Code quality checks)
  ↓
  Merge to scrape
  ↓
  (Dev Docker image built)
  ↓
  Manual: SSH to dev server and run:
  cd /app/tiktok-scraper && ./start.sh dev
```

**Production Flow:**
```
scrape branch → PR to main
  ↓
  (All checks: code quality, tests, security)
  ↓
  Merge to main
  ↓
  (Production Docker image built)
  ↓
  Manual: SSH to prod server and run:
  cd /app/tiktok-scraper && ./start.sh prod
```

Or use GitHub releases:
```bash
git tag v1.0.0
git push origin v1.0.0
# Triggers production deployment automatically
```

---

## Server Setup

### New Server Preparation

1. **Install Docker:**
   ```bash
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   ```

2. **Install Docker Compose:**
   ```bash
   sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose
   ```

3. **Clone repository:**
   ```bash
   sudo mkdir -p /app
   cd /app
   sudo git clone https://github.com/yourusername/tiktok-scraper.git
   cd tiktok-scraper
   ```

4. **Create `.env` file:**
   ```bash
   sudo nano .env
   ```
   Add:
   ```env
   DEBUG=False
   MS_TOKEN=your_token
   HEADLESS=True
   ```

5. **Set up firewall (if applicable):**
   ```bash
   sudo ufw allow 5000/tcp
   ```

6. **Start application:**
   ```bash
   sudo ./start.sh prod
   ```

### Reverse Proxy Setup (Recommended)

For production, use Nginx as a reverse proxy:

```bash
# Install Nginx
sudo apt-get install nginx

# Create Nginx config
sudo tee /etc/nginx/sites-available/tiktok-scraper > /dev/null <<EOF
upstream tiktok_api {
    server localhost:5000;
}

server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://tiktok_api;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/tiktok-scraper /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### SSL/TLS with Let's Encrypt (Optional)

```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

---

## Scaling Considerations

### Increase Workers
Edit `docker-compose.prod.yml`:
```yaml
command: python -m uvicorn app:app --host 0.0.0.0 --port 5000 --workers 4
```

### Load Balancing
Use multiple app instances with load balancer:
```yaml
services:
  app1:
    # ... config
    ports:
      - "5001:5000"
  
  app2:
    # ... config
    ports:
      - "5002:5000"
```

Then Nginx distributes traffic between them.

### Database/Cache (Future)
When adding Redis or PostgreSQL:
```bash
docker-compose up -d redis postgres
```

---

## Monitoring & Logs

### View Logs
```bash
./start.sh logs                          # All logs
docker-compose logs tiktok-scraper       # Dev logs
docker-compose -f docker-compose.prod.yml logs tiktok-scraper  # Prod logs
```

### Health Check
```bash
curl http://localhost:5000/api/status
```

Expected response:
```json
{
  "is_running": false,
  "progress": 0,
  "total": 0,
  "current_url": null,
  "error": null
}
```

### Performance Monitoring
Visit the `/docs` endpoint for Swagger UI and test endpoints.

---

## Troubleshooting

### Port Already in Use
```bash
# Change port in docker-compose.yml
# Or find and kill existing process
lsof -i :5000
kill -9 <PID>
```

### Image Pull Failures
```bash
# Check Docker registry access
docker login ghcr.io
docker pull ghcr.io/yourusername/tiktok-scraper:prod-latest
```

### Scraping Failures
- Check `MS_TOKEN` is valid (get from tiktok.com)
- Verify network connectivity
- Check logs: `./start.sh logs`

### Container Exits Immediately
```bash
docker-compose up  # Run in foreground to see errors
```

### Volume Permission Issues
```bash
# Fix permissions
sudo chown -R $(whoami):$(whoami) ./exports ./logs
```

---

## Backup & Restore

### Backup Exports
```bash
# Create backup
tar -czf tiktok-scraper-backup-$(date +%Y%m%d).tar.gz exports/

# List backups
ls -lh tiktok-scraper-backup-*.tar.gz
```

### Restore from Backup
```bash
# Extract backup
tar -xzf tiktok-scraper-backup-20240101.tar.gz

# Restart container
./start.sh stop
./start.sh prod
```

---

## Updates & Maintenance

### Update Application
```bash
# Pull latest code
git pull origin main

# Rebuild and restart
./start.sh prod
```

### Update Dependencies
```bash
# Edit requirements.txt and rebuild
./start.sh build
./start.sh prod
```

### Schedule Cleanup
```bash
# Add to crontab (runs weekly)
0 0 * * 0 docker system prune -f
```

---

## References

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [GitHub Actions Documentation](https://docs.github.com/actions)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
