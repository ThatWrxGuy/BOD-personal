#!/bin/bash
# =============================================================================
# PSIE Local Bootstrap Script
# =============================================================================
# This script helps set up PSIE for local development.
# =============================================================================

set -e

echo "============================================"
echo "PSIE Local Bootstrap"
echo "============================================"

# Check if .env exists
if [ ! -f .env ]; then
    echo "📄 No .env file found. Creating from .env.example..."
    cp .env.example .env
    echo "✅ Created .env file"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env and configure required settings:"
    echo "   - SECRET_KEY (required for production)"
    echo "   - OPENAI_API_KEY or ANTHROPIC_API_KEY (required for AI)"
    echo ""
    echo "Then run this script again."
    exit 0
fi

echo "📄 .env file exists"

# Check Python
if command -v python3 &> /dev/null; then
    echo "✅ Python3 found"
else
    echo "❌ Python3 not found. Please install Python 3.10+"
    exit 1
fi

# Check if virtual env exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Created virtual environment"
fi

# Activate virtual env
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt > /dev/null 2>&1
echo "✅ Installed dependencies"

# Run config check
echo ""
echo "🔍 Checking configuration..."
python scripts/check_config.py

echo ""
echo "============================================"
echo "Setup complete!"
echo "============================================"
echo ""
echo "To start the backend:"
echo "  source venv/bin/activate"
echo "  uvicorn app.main:app --reload"
echo ""
echo "To start the frontend:"
echo "  cd frontend"
echo "  npm install"
echo "  npm run dev"
echo ""
