# ==============================================================================
# Dockerfile for FindIt — College Lost & Found Portal
# Subject: DevOps and Kubernetes (ISE-2)
# ==============================================================================

FROM python:3.13-slim

# Prevent Python from writing .pyc files & buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=5000

WORKDIR /app

# Install system build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project code
COPY . .

# Create instance and upload directories
RUN mkdir -p instance uploads

# Expose port 5000
EXPOSE 5000

# Healthcheck to verify service availability
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5000/ || exit 1

# Start Flask Application
CMD ["python", "app.py"]
