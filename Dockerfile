# ---------- Dockerfile (full Python image) ----------
# Base image: official Python 3.12
FROM python:3.12

# Set working directory inside the container
WORKDIR /app

# Copy requirements first (Docker caches this layer if requirements don't change)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files
COPY app.py .
COPY templates/ templates/
COPY static/ static/

# Create a directory for the SQLite database
# This path matches the DATA_DIR environment variable below
RUN mkdir -p /app/data

# Set environment variables
ENV DATA_DIR=/app/data
ENV FLASK_PORT=5000

# Expose the Flask port
EXPOSE 5000

# Health check: hit the /health endpoint every 30 seconds
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')" || exit 1

# Start the application
CMD ["python", "app.py"]
