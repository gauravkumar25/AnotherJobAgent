#!/bin/bash

# Career Agents UI Launcher
# Quick start script for the web interface

set -e

echo "🚀 Career Agents UI Launcher"
echo ""

# Check if XAI_API_KEY is set
if [ -z "$XAI_API_KEY" ]; then
    echo "⚠️  XAI_API_KEY not found in environment"
    echo ""
    echo "Please set your API key:"
    echo "  export XAI_API_KEY='your-key-here'"
    echo ""
    echo "Or create a .env file:"
    echo "  echo 'XAI_API_KEY=your-key-here' > .env"
    echo ""

    # Try loading from .env if it exists
    if [ -f .env ]; then
        echo "📁 Loading from .env file..."
        export $(cat .env | grep -v '^#' | xargs)

        if [ -z "$XAI_API_KEY" ]; then
            echo "✗ XAI_API_KEY not found in .env file"
            exit 1
        else
            echo "✓ Loaded XAI_API_KEY from .env"
        fi
    else
        exit 1
    fi
else
    echo "✓ XAI_API_KEY found in environment"
fi

echo ""

# Check if requirements are installed
if ! python -c "import flask" 2>/dev/null; then
    echo "📦 Installing requirements..."
    pip install -r requirements.txt
    echo ""
fi

# Start the server
echo "🌐 Starting server..."
echo "   → http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop"
echo ""

python app.py
