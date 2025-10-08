#!/bin/bash

# Smart Car Trip Tracker - Quick Setup Script

echo "🚗 Smart Car Trip Tracker - Setup Script"
echo "========================================="

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

# Check if pip is installed
if ! command -v pip &> /dev/null && ! command -v pip3 &> /dev/null; then
    echo "❌ pip is not installed. Please install pip first."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️ Creating environment file..."
    cp config/.env.example .env
    echo "✅ Please edit .env file with your settings"
fi

# Create data directory
mkdir -p data

echo ""
echo "✅ Setup complete!"
echo ""
echo "🚀 To start the server:"
echo "   source .venv/bin/activate"
echo "   cd src && python3 main.py"
echo ""
echo "📖 Or use uvicorn directly:"
echo "   cd src && uvicorn main:app --host 127.0.0.1 --port 8001"
echo ""
echo "🌐 API will be available at:"
echo "   - Main API: http://localhost:8001"
echo "   - Documentation: http://localhost:8001/docs"
echo "   - Health Check: http://localhost:8001/health"