#!/bin/bash

# GPS Scintillation Data Automation Setup and Run Script

echo "🚀 GPS Scintillation Data Automation Setup"
echo "=========================================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed. Please install Python3 first."
    exit 1
fi

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip3 first."
    exit 1
fi

# Install required packages
echo "📦 Installing required Python packages..."
pip3 install -r requirements_automation.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Check if API server is running
echo "🔍 Checking if API server is running..."
if curl -s http://127.0.0.1:8000 > /dev/null; then
    echo "✅ API server is running"
else
    echo "⚠️  API server is not running. Please start it with:"
    echo "   cd /Users/user/Desktop/s4c-api-serives"
    echo "   docker-compose up -d"
    echo ""
    echo "Or start the backend manually:"
    echo "   cd /Users/user/Desktop/s4c-api-serives/backend"
    echo "   python main.py"
    echo ""
    read -p "Do you want to continue anyway? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Run the automation script
echo "🏃 Starting GPS data automation..."
echo "Press Ctrl+C to stop"
echo ""

python3 automated_processor.py
