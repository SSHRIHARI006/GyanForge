#!/bin/bash

# GyanForge Development Setup Script

echo "🎓 Setting up GyanForge development environment..."

# Check prerequisites
check_command() {
    if ! command -v $1 &> /dev/null; then
        echo "❌ Error: $1 is not installed. Please install $1 and try again."
        exit 1
    fi
}

echo "🔍 Checking prerequisites..."
check_command "python3"
check_command "node"
check_command "npm"
check_command "git"

# Setup backend
echo "🐍 Setting up backend..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Setup environment file
if [ ! -f ".env" ]; then
    echo "⚙️ Creating backend .env file..."
    cp .env.example .env
    echo "🔑 Please edit backend/.env with your API keys:"
    echo "   - GEMINI_API_KEY"
    echo "   - PINECONE_API_KEY"
    echo ""
fi

cd ../

# Setup frontend
echo "⚛️ Setting up frontend..."
cd frontend

# Install dependencies
echo "📥 Installing Node.js dependencies..."
npm install

# Setup environment file
if [ ! -f ".env" ]; then
    echo "⚙️ Creating frontend .env file..."
    cp .env.example .env
fi

cd ../

echo "✅ Setup complete!"
echo ""
echo "🚀 To start development:"
echo "   1. Backend: cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
echo "   2. Frontend: cd frontend && npm start"
echo ""
echo "📝 Don't forget to:"
echo "   - Add your API keys to backend/.env"
echo "   - Configure frontend/.env if using custom API URL"
echo ""
echo "📖 Visit http://localhost:3000 for the frontend"
echo "📊 Visit http://localhost:8000/docs for API documentation"
