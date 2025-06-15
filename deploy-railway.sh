#!/bin/bash

# Railway Ollama Deployment Script
echo "🚀 Railway Ollama Deployment Setup"
echo "=================================="

# Check if railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Installing..."

    # Detect OS and install Railway CLI
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            brew install railway
        else
            echo "Please install Homebrew first: https://brew.sh"
            exit 1
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        curl -fsSL https://railway.app/install.sh | sh
    else
        echo "Please install Railway CLI manually: https://docs.railway.app/develop/cli"
        exit 1
    fi
fi

echo "✅ Railway CLI is ready"

# Login to Railway
echo "🔑 Logging into Railway..."
railway login

# Create new project
echo "📦 Creating new Railway project..."
railway init

# Set environment variables
echo "⚙️  Setting environment variables..."
railway variables set OLLAMA_HOST=0.0.0.0
railway variables set OLLAMA_ORIGINS=*

# Deploy the project
echo "🚀 Deploying to Railway..."
railway up

echo ""
echo "🎉 Deployment initiated!"
echo "📊 Monitor your deployment at: https://railway.app/dashboard"
echo ""
echo "⏳ The deployment will take several minutes to:"
echo "   1. Build the Docker image"
echo "   2. Start Ollama server"
echo "   3. Download the AI models (qwen2.5:7b and deepseek-r1:14b)"
echo ""
echo "🔗 Once complete, your Ollama API will be available at:"
echo "   https://your-project-name.up.railway.app"
echo ""
echo "🧪 Test your deployment with:"
echo "   curl https://your-project-name.up.railway.app/api/tags"
