# Setup Summary - Docker & GitHub Actions

## What Was Created

This summary documents all the new files and features added for containerization and CI/CD deployment.

### Files Created

#### 1. **Docker Configuration**
- **`Dockerfile`** - Multi-stage Docker image (1.47GB with Playwright browsers)
  - Python 3.11 slim base
  - System dependencies for Chromium, Firefox
  - All Python packages from requirements.txt
  
- **`docker-compose.yml`** - Development environment
  - Hot reload on file changes
  - Source code mounted
  - DEBUG=True
  
- **`docker-compose.prod.yml`** - Production environment
  - 2 uvicorn workers
  - Health checks
  - Persistent named volumes
  - Restart policy
  
- **`.dockerignore`** - Excludes unnecessary files from build context

#### 2. **Startup Scripts**
- **`start.sh`** (updated) - Unified startup script with 8 commands
  - `./start.sh dev` - Docker dev with hot reload
  - `./start.sh prod` - Docker production
  - `./start.sh local` - Local Python venv (legacy)
  - `./start.sh build` - Build Docker image
  - `./start.sh logs` - View logs
  - `./start.sh stop` - Stop containers
  - `./start.sh shell` - Enter container shell
  - `./start.sh clean` - Clean up containers/volumes
  
- **`Makefile`** - Convenient make commands
  - `make dev` - Start development
  - `make prod` - Start production
  - `make build` - Build image
  - `make logs` - View logs
  - And more...

#### 3. **GitHub Actions Workflows** (`.github/workflows/`)
- **`dev-deploy.yml`** - Development CI/CD
  - Triggers: Push to `scrape`/`develop`, PRs, manual
  - Builds Docker image, runs tests, deploys
  - Posts status to PRs
  
- **`prod-deploy.yml`** - Production CI/CD
  - Triggers: Push to `main`, version tags, manual
  - Comprehensive checks: build, test, security scan
  - Creates deployment record
  - Slack notifications (optional)
  
- **`code-quality.yml`** - Code quality checks
  - Runs on all PRs and pushes
  - Black, isort, flake8, pylint
  - Docker build test
  - Syntax validation

#### 4. **Documentation**
- **`DOCKER.md`** - Docker usage guide
  - Development vs production
  - Volume management
  - Troubleshooting
  - Performance notes
  
- **`DEPLOYMENT-GUIDE.md`** - Complete deployment guide
  - Quick start instructions
  - Server setup (Linux)
  - Nginx reverse proxy
  - SSL/TLS setup
  - Monitoring and troubleshooting
  - Scaling considerations
  
- **`.github/WORKFLOWS.md`** - GitHub Actions documentation
  - Workflow overview
  - Setup instructions
  - Slack notifications
  - Branch strategy
  - Versioning & releases
  - Troubleshooting

---

## Quick Start Guide

### 1. Local Development (Recommended)

```bash
# Make sure you're on the scrape branch
git checkout scrape

# Ensure .env has MS_TOKEN (from tiktok.com)
echo "MS_TOKEN=your_token_here" >> .env

# Start development with Docker
./start.sh dev

# In another terminal, watch logs
./start.sh logs

# Access API
# - Web UI: http://localhost:5000
# - Docs: http://localhost:5000/docs
# - API: http://localhost:5000/api/scrape (POST)

# Stop when done
./start.sh stop
```

### 2. Production Deployment

```bash
# Option A: Using start script
./start.sh prod

# Option B: Using make
make prod-build && make prod

# Option C: Manual Docker
docker-compose -f docker-compose.prod.yml up -d

# Verify
curl http://localhost:5000/api/status
```

---

## GitHub Actions Workflows

### Code Quality (Automatic on PRs)
Every pull request automatically gets:
- Syntax checks
- Code linting (Black, isort, flake8)
- Docker build test
- Dependency validation

### Development Deployment
When you push to `scrape` or `develop`:
1. Code quality checks run
2. Docker image built and pushed to GitHub Container Registry
3. Manual deployment instructions provided

**To deploy after push:**
```bash
# SSH into dev server
cd /app/tiktok-scrape
git pull origin scrape
./start.sh dev
```

### Production Deployment
When you push to `main` or create a release:
1. All checks run (code quality + security scan)
2. Docker image built and pushed
3. Slack notification sent (if webhook configured)

**To deploy after push:**
```bash
# SSH into prod server
cd /app/tiktok-scrape
git pull origin main
./start.sh prod
```

Or create a release:
```bash
git tag v1.0.0
git push origin v1.0.0
# Workflow triggers automatically
```

---

## Environment Variables

### Development (`.env` file)
```env
DEBUG=True
HOST=127.0.0.1
PORT=5000
MS_TOKEN=your_token_here
HEADLESS=True
```

### Production (GitHub Secrets + `.env`)
```env
DEBUG=False
HOST=0.0.0.0
PORT=5000
MS_TOKEN=your_token_here
HEADLESS=True
MAX_COMMENTS=500
```

**Add to GitHub Secrets:**
1. Settings → Secrets and variables → Actions
2. Add `MS_TOKEN`
3. Add `SLACK_WEBHOOK_URL` (optional)

---

## Docker Image Details

**Size:** 1.47GB (includes Playwright browsers)

**Includes:**
- Python 3.11-slim base image
- Chromium browser (for evasion detection)
- Firefox browser (fallback)
- All system dependencies for headless browsers
- FastAPI, uvicorn, aiofiles, pydantic, pandas
- Playwright stealth plugin

**Layers:**
1. System dependencies (apt-get)
2. Python packages (pip)
3. Playwright browsers (playwright install)
4. Application code
5. Export/log directories

---

## Commands Reference

### start.sh (Recommended)
```bash
./start.sh dev              # Dev with Docker
./start.sh prod             # Production with Docker
./start.sh local            # Local venv (legacy)
./start.sh build            # Build Docker image
./start.sh logs             # View logs
./start.sh stop             # Stop containers
./start.sh shell            # Enter container
./start.sh clean            # Remove containers
./start.sh help             # Show help
```

### Makefile
```bash
make dev                    # Dev with Docker
make prod                   # Production
make prod-build             # Build prod image
make build                  # Build image
make logs                   # View logs
make stop                   # Stop containers
make shell                  # Enter container
make clean                  # Remove containers
```

### Docker Compose (Manual)
```bash
# Development
docker-compose up                          # Foreground
docker-compose up -d                       # Background
docker-compose logs -f                     # View logs
docker-compose down                        # Stop

# Production
docker-compose -f docker-compose.prod.yml up -d
docker-compose -f docker-compose.prod.yml logs -f
docker-compose -f docker-compose.prod.yml down
```

---

## Branch Strategy

```
┌─ feature-branches
│   └─ (Code quality checks)
│
├─ scrape (development)
│   ├─ (Dev Docker image built)
│   └─ Manual deploy: ./start.sh dev
│
└─ main (production)
    ├─ (All checks + security scan)
    ├─ Docker image pushed
    └─ Manual deploy: ./start.sh prod
```

---

## Deployment Checklist

### Before First Deployment

- [ ] Clone repository
- [ ] Create `.env` with `MS_TOKEN`
- [ ] Test locally: `./start.sh dev`
- [ ] Push to GitHub
- [ ] Verify workflows run successfully

### Dev Deployment

- [ ] Push to `scrape` branch
- [ ] Check Actions workflow succeeds
- [ ] SSH to dev server
- [ ] Run: `cd /app/tiktok-scraper && git pull origin scrape && ./start.sh dev`
- [ ] Test: `curl http://localhost:5000/api/status`

### Prod Deployment

- [ ] Merge `scrape` → `main` (via PR)
- [ ] Check all workflows pass
- [ ] Option A: Create release tag `v1.0.0`
- [ ] Option B: Push to main and manually deploy
- [ ] SSH to prod server
- [ ] Run: `cd /app/tiktok-scrape && git pull origin main && ./start.sh prod`
- [ ] Test: `curl http://localhost:5000/api/status`
- [ ] Monitor logs: `./start.sh logs`

### Slack Notifications (Optional)

- [ ] Create Slack Incoming Webhook
- [ ] Add `SLACK_WEBHOOK_URL` to GitHub Secrets
- [ ] Production deployments will notify Slack

---

## Next Steps

1. **Push this to GitHub:**
   ```bash
   git add .
   git commit -m "feat: add Docker setup and GitHub Actions CI/CD"
   git push origin scrape
   ```

2. **Add secrets to GitHub:**
   - Settings → Secrets and variables → Actions
   - Add `MS_TOKEN`
   - Add `SLACK_WEBHOOK_URL` (optional)

3. **Create dev/prod servers:**
   - Install Docker & Docker Compose
   - Clone repo
   - Create `.env`
   - Run `./start.sh dev` or `./start.sh prod`

4. **Monitor deployments:**
   - Go to Actions tab to view workflow runs
   - Check logs if something fails
   - Subscribe to Slack notifications

---

## Troubleshooting

### Docker image won't build
```bash
# Check Docker is running
docker ps

# Rebuild with verbose output
docker build -t tiktok-scraper:latest .

# Check disk space
df -h /var/lib/docker
```

### Port 5000 in use
```bash
# Find process using port
lsof -i :5000

# Kill it
kill -9 <PID>

# Or change port in docker-compose.yml
```

### Image too large
1.47GB is normal (includes browsers & system libs)
```bash
# Check image size
docker images | grep tiktok

# Clean old images
docker image prune -a
```

### Workflows not triggering
- Check branch name matches trigger conditions
- Verify `.github/workflows/` exists
- Commit must push to trigger (not just create)

### GitHub Actions secrets not working
- Add secrets to Settings → Secrets and variables
- Don't commit `.env` with real tokens
- Secrets are injected at runtime, not visible in logs

---

## References

- **Docker:** [docs.docker.com](https://docs.docker.com)
- **Docker Compose:** [docs.docker.com/compose](https://docs.docker.com/compose)
- **GitHub Actions:** [docs.github.com/actions](https://docs.github.com/actions)
- **FastAPI:** [fastapi.tiangolo.com](https://fastapi.tiangolo.com)
- **Playwright:** [playwright.dev](https://playwright.dev)

---

## Support

- Check DOCKER.md for Docker-specific issues
- Check DEPLOYMENT-GUIDE.md for server setup
- Check .github/WORKFLOWS.md for GitHub Actions issues
- Check logs: `./start.sh logs`
- Review Actions tab on GitHub for workflow logs
