# ─── Stage: Build ──────────────────────────────────────────────────────────────
# Use a slim Python 3.11 image to keep the final image size down
FROM python:3.11-slim

# Prevent Python from writing .pyc files to disk and ensure stdout/stderr are
# unbuffered so logs are immediately visible in `kubectl logs`.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Create and set the working directory
WORKDIR /app

# Install system dependencies needed by psycopg2-binary (Postgres adapter)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file first so that Docker layer caching means we only
# re-install deps when requirements.txt changes, not on every code change.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application source code
COPY app/ ./app/
COPY seed.py .

# Expose the application port
EXPOSE 8000

# Run the FastAPI application with Uvicorn
# We bind to 0.0.0.0 so Kubernetes can route traffic into the pod.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
