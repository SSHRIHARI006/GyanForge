#!/bin/bash

# Render startup script for GyanForge backend

echo "🚀 Starting GyanForge backend on Render..."

# Set up Python path
export PYTHONPATH=/opt/render/project/src/backend:$PYTHONPATH

# Navigate to backend directory
cd backend

# Create database tables if they don't exist
echo "📁 Setting up database..."
python3 -c "
from app.db.session import engine
from app.models.models import *
from sqlmodel import SQLModel

print('Creating database tables...')
SQLModel.metadata.create_all(engine)
print('Database setup complete!')
"

# Start the application
echo "🌟 Starting FastAPI application..."
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT
