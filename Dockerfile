# Simple Docker build for GyanForge (avoiding dependency conflicts)
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip

# Install core dependencies manually (avoiding conflicts)
RUN pip install fastapi==0.104.1 \
    uvicorn[standard]==0.24.0 \
    pydantic==2.4.2 \
    sqlmodel==0.0.8 \
    sqlalchemy==1.4.41 \
    python-jose[cryptography]==3.3.0 \
    passlib[bcrypt]==1.7.4 \
    python-multipart==0.0.6 \
    psycopg2-binary==2.9.9 \
    google-generativeai==0.3.2 \
    python-dotenv==1.0.0 \
    requests==2.31.0 \
    PyJWT==2.8.0 \
    psutil==5.9.6

# Copy backend application code
COPY backend/ .

# Create necessary directories
RUN mkdir -p storage/assignments storage/pdfs

# Expose port
EXPOSE 8000

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
