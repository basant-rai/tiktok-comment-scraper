# Docker Setup Guide

This project includes Docker configurations for both development and production environments.

## Prerequisites

- Docker >= 20.10
- Docker Compose >= 2.0

## File Overview

- **Dockerfile** - Multi-stage optimized image for both dev and prod
- **docker-compose.yml** - Development environment with hot reload
- **docker-compose.prod.yml** - Production environment with healthcheck and optimizations
- **Makefile** - Convenient commands for common Docker tasks
- **.dockerignore** - Excludes unnecessary files from build context

## Development

Start the development environment with hot reload:

```bash
make dev
# or
docker-compose up
```

The API will be available at `http://localhost:5000`. Changes to Python files will automatically reload.

Access the container shell:

```bash
make shell
```

View logs:

```bash
make logs
```

Stop the container:

```bash
make stop
```

## Production

Build the production image:

```bash
make prod-build
```

Start the production environment:

```bash
make prod
```

The API runs with:
- 2 uvicorn workers
- Automatic restart on failure
- Health checks every 30 seconds
- Named volumes for exports and logs (persist across restarts)

View production logs:

```bash
make prod-logs
```

## Environment Variables

Create a `.env` file in the project root (git-ignored):

```env
DEBUG=False
HOST=0.0.0.0
PORT=5000
MS_TOKEN=your_tiktok_mstoken_here
HEADLESS=True
MAX_COMMENTS=500
TIMEOUT=60
RETRIES=3
OUTPUT_DIR=exports
LOGS_DIR=logs
```

For production, ensure `MS_TOKEN` is set to a valid token (see [QUICKSTART.md](QUICKSTART.md) for how to obtain it).

## Volumes

**Development:**
- Source code is mounted live (hot reload)
- `./exports` - Scraped data (local directory)
- `./logs` - Application logs (local directory)

**Production:**
- `exports` - Named volume for exports (persistent)
- `logs` - Named volume for logs (persistent)

Use `docker volume ls` to see all volumes, and `docker volume inspect <name>` to see details.

## API Endpoints

Once running, access the API at `http://localhost:5000`:

- `GET /` - Web UI
- `GET /docs` - OpenAPI documentation
- `POST /api/scrape` - Scrape TikTok video comments
- `GET /api/comments/{video_id}` - Retrieve cached comments
- `GET /api/exports` - List exported files
- `GET /api/download/{filename}` - Download export file
- `GET /api/status` - Check scraping status
- `POST /api/validate-url` - Validate TikTok URL

## Troubleshooting

**Container won't start:**
```bash
docker-compose logs tiktok-scraper
```

**Port 5000 already in use:**
Edit `docker-compose.yml` and change `"5000:5000"` to `"5001:5000"` (or any available port).

**Rebuild image to pick up dependency changes:**
```bash
make dev-build  # Dev with rebuild
docker-compose -f docker-compose.prod.yml build --no-cache  # Prod with no cache
```

**Export data not persisting in production:**
Ensure the named volumes exist:
```bash
docker volume ls | grep tiktok
```

**Clear everything and start fresh:**
```bash
make clean
make dev-build
```

## Performance Notes

- **Headless mode**: Faster but may be detected by TikTok. Use visible browser if needed (requires X11 forwarding or desktop display).
- **Playwright browsers**: Image includes Chromium and Firefox. Size is ~1.2GB.
- **MS_TOKEN expiry**: TikTok tokens expire periodically. Refresh in your browser if scraping fails.
