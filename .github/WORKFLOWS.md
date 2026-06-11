# GitHub Actions Workflows

This project includes automated CI/CD workflows for testing, building, and deploying to development and production environments.

## Workflows Overview

### 1. Code Quality (`code-quality.yml`)
Runs on all push and pull requests to ensure code quality.

**Triggers:**
- Push to `main`, `scrape`, or `develop` branches
- Pull requests to `main`, `scrape`, or `develop` branches

**Jobs:**
- **Lint**: Checks code formatting with Black, isort, flake8, pylint
- **Syntax Check**: Verifies Python files compile without syntax errors
- **Dependencies**: Installs and lists all dependencies
- **Docker Build Test**: Validates Dockerfile builds successfully

**Passing the Check:**
All jobs run in `continue-on-error: true` mode to warn about issues without blocking merges. If you want stricter checks, edit the workflow file and remove the `continue-on-error` lines.

---

### 2. Development Deployment (`dev-deploy.yml`)
Builds and deploys to development environment.

**Triggers:**
- Push to `scrape` or `develop` branches
- Pull requests (image build only, no deployment)
- Manual trigger (`workflow_dispatch`)

**Environment:**
- Registry: GitHub Container Registry (ghcr.io)
- Image tag: `dev-latest`, `scrape-<sha>`, etc.

**Jobs:**
1. **Build**: Builds Docker image and pushes to registry
2. **Test**: Runs syntax checks and linting
3. **Deploy**: Provides deployment instructions
4. **Notify**: Posts deployment status

**Deployment Steps (Manual):**
After workflow succeeds, SSH into your development server and run:

```bash
cd /app/tiktok-scraper
git pull origin scrape
./start.sh dev
```

---

### 3. Production Deployment (`prod-deploy.yml`)
Builds, tests, and deploys to production.

**Triggers:**
- Push to `main` branch
- Git tags (e.g., `v1.0.0`)
- Manual trigger (`workflow_dispatch`)

**Environment:**
- Registry: GitHub Container Registry (ghcr.io)
- Image tag: `prod-latest`, `v1.0.0`, etc.

**Jobs:**
1. **Build**: Builds Docker image and pushes to registry
2. **Test**: Runs all code checks
3. **Security**: Scans image with Trivy for vulnerabilities
4. **Deploy**: Creates deployment record (awaits manual confirmation)
5. **Notify**: Sends Slack notification (optional)

**Deployment Steps (Manual):**
After workflow succeeds, SSH into your production server and run:

```bash
cd /app/tiktok-scraper
git pull origin main
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d
```

Or use the start script:
```bash
./start.sh prod
```

**Verify:**
```bash
curl http://localhost:5000/api/status
```

---

## Setup Instructions

### 1. Container Registry Authentication

The workflows push images to GitHub Container Registry. This is automatic if you:
- Have a GitHub token with `packages:write` permission (enabled by default for GitHub Actions)
- Have the repository set to public or internal (private repos need additional setup)

**For Private Repositories:**
Create a Personal Access Token (PAT):
1. Go to GitHub Settings → Developer Settings → Personal Access Tokens
2. Create token with `write:packages` scope
3. Add as secret `GHCR_TOKEN` (optional, `GITHUB_TOKEN` usually works)

---

### 2. Slack Notifications (Optional)

To receive Slack notifications on production deployments:

1. Create a Slack Webhook URL:
   - Go to your Slack workspace → Settings → Apps
   - Add "Incoming Webhooks"
   - Create a webhook for your channel
   - Copy the webhook URL

2. Add to repository secrets:
   - Go to Settings → Secrets and variables → Actions
   - Create secret named `SLACK_WEBHOOK_URL`
   - Paste your webhook URL

If not set, Slack notifications will be skipped gracefully.

---

### 3. Environment Variables

The workflows automatically handle:
- **MS_TOKEN**: Set via repository secrets or `.env` file
- **DEBUG**: Automatically set based on environment (True for dev, False for prod)
- **PORT**: Defaults to 5000

**To add secrets:**
1. Go to repository Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Add `MS_TOKEN` with your TikTok token
4. Add any other secrets your app needs

Secrets are available to all workflows automatically.

---

## Workflow Runs

### View Workflow Status
1. Go to repository → Actions tab
2. Click on a workflow to see its runs
3. Click on a run to see detailed logs

### Manual Workflow Trigger
1. Go to Actions tab
2. Select a workflow (e.g., "Deploy to Production")
3. Click "Run workflow"
4. Select branch (defaults to `main`)
5. Click "Run workflow"

### View Logs
Click on a failed job to see detailed error messages.

---

## Branch Strategy

**Recommended workflow:**

```
feature-branch → scrape (dev) → main (prod)
```

- **Feature branches**: Make PRs to `scrape` branch
  - Triggers code quality checks
  - Dev Docker image built
  
- **Scrape branch** (development):
  - Merges from feature PRs
  - Triggers dev deployment
  - Pre-production testing
  
- **Main branch** (production):
  - Merges from scrape branch (or create release)
  - Triggers production deployment
  - Must pass all checks
  - Consider requiring status checks to pass

---

## Versioning & Releases

For production, use semantic versioning:

1. Create a release on GitHub (e.g., `v1.0.0`)
2. This triggers `prod-deploy.yml` automatically
3. Docker image tagged as `v1.0.0`, `1.0`, `1`, and `prod-latest`

**Create release via command line:**
```bash
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

---

## Troubleshooting

### Workflow won't trigger
- Check branch name matches the trigger condition
- Ensure `.github/workflows/` directory exists
- Commits must trigger the workflow (check branch filters)

### Docker image not found after build
- Check image is properly pushed: `docker pull ghcr.io/yourname/tiktok-scraper:dev-latest`
- Verify token has `packages:write` permission
- Check Container Registry visibility (Settings → Packages and data → Container Registry)

### Security scan failed
- Review Trivy results in "Security" tab
- Minor vulnerabilities can be ignored; focus on critical/high severity
- Update dependencies if needed

### Deployment fails
- Check workflow logs for error messages
- Verify secrets are set (`MS_TOKEN`)
- Ensure server has Docker/Docker Compose installed
- Check disk space on deployment server

---

## Customization

### Add More Checks
Edit workflow files to add:
- Unit tests: Add `pytest` step
- Integration tests: Add `docker-compose up` then test
- Performance tests: Add benchmarking
- Accessibility checks: Add axe/lighthouse

### Change Deployment Server
Modify the deploy jobs to:
- Use SSH action to connect to server
- Run deployment commands via SSH
- Or use deployment platform API (AWS, Heroku, DigitalOcean, etc.)

### Add Environment-Specific Variables
```yaml
env:
  DATABASE_URL: ${{ secrets.DATABASE_URL }}
  API_KEY: ${{ secrets.API_KEY }}
```

---

## References

- [GitHub Actions Documentation](https://docs.github.com/actions)
- [Docker Build Push Action](https://github.com/docker/build-push-action)
- [GitHub Container Registry](https://docs.github.com/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- [Slack Incoming Webhooks](https://api.slack.com/messaging/webhooks)
