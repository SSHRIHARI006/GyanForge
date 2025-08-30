# Simple Docker build for GyanForge (staged installation)
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install build tools
RUN pip install --upgrade pip setuptools wheel

# Install dependencies in stages to avoid conflicts
# Stage 1: Core web framework
RUN pip install fastapi uvicorn[standard]

# Stage 2: Data validation and ORM
RUN pip install pydantic sqlmodel sqlalchemy==1.4.53

# Stage 3: Authentication and security
RUN pip install python-jose[cryptography] passlib[bcrypt] PyJWT

# Stage 4: HTTP and utilities
RUN pip install python-multipart python-dotenv requests psutil

# Stage 5: AI and database (optional - skip if conflicts)
RUN pip install google-generativeai || echo "Skipping AI package"
RUN pip install psycopg2-binary || echo "Skipping PostgreSQL"

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
