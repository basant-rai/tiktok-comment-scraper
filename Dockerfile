FROM python:3.11-slim

WORKDIR /app

# Copy requirements first (for better caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers and all system dependencies
RUN playwright install chromium firefox && \
    playwright install-deps chromium firefox

# Copy application code
COPY . .

# Create directories for exports and logs
RUN mkdir -p exports logs

# Expose API port
EXPOSE 5000

# Default entrypoint - can be overridden
CMD ["python", "app.py"]
