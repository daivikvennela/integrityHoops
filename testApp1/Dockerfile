# Dockerfile for IntegrityHoops Basketball Dashboard
# For Docker-based deployments (AWS ECS, Google Cloud Run, etc.)

FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY config/requirements.txt /app/config/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r config/requirements.txt

# Copy application files
COPY . /app/

# Create necessary directories
RUN mkdir -p /app/data /app/data/uploads /app/data/processed /tmp/uploads /tmp/processed

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=src.core.app
ENV FLASK_ENV=production

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/')"

# Run the application
CMD ["gunicorn", "--chdir", "testApp1", "--workers", "4", "--bind", "0.0.0.0:8000", "src.core.app:app", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-"]

