#!/bin/bash

# Deployment script for Chronology Agent
# This script helps you deploy the application in different configurations

set -e

echo "🚀 Chronology Agent Deployment Script"
echo "======================================"

# Create necessary directories
mkdir -p uploads
mkdir -p .env

# Copy environment file if it doesn't exist
if [ ! -f .env ]; then
    echo "📄 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your configuration before proceeding!"
    echo "   Key settings to update:"
    echo "   - Change default passwords"
    echo "   - Set your OpenAI API key (if using OpenAI)"
    echo "   - Configure Langfuse settings"
    read -p "Press Enter after editing .env to continue..."
fi

echo
echo "Choose deployment option:"
echo "1) Simple (App + Ollama only)"
echo "2) Full (App + Ollama + Langfuse monitoring)"
echo "3) Local development (no Docker)"
echo "4) Pull and setup Ollama models"
echo "5) Stop all services"
echo

read -p "Enter your choice (1-5): " choice

case $choice in
    1)
        echo "🐳 Starting simple deployment..."
        docker-compose -f docker-compose.simple.yml up -d --build
        echo "✅ Services started!"
        echo "📱 Chronology Agent: http://localhost:8501"
        echo "🤖 Ollama API: http://localhost:11434"
        ;;
    2)
        echo "🐳 Starting full deployment with monitoring..."
        docker-compose -f docker-compose.full.yml up -d --build
        echo "✅ Services started!"
        echo "📱 Chronology Agent: http://localhost:8501"
        echo "🤖 Ollama API: http://localhost:11434"
        echo "📊 Langfuse Dashboard: http://localhost:3000"
        echo "💾 MinIO Console: http://localhost:9091"
        ;;
    3)
        echo "💻 Setting up local development..."

        # Check if Python is installed
        if ! command -v python3 &> /dev/null; then
            echo "❌ Python 3 is required. Please install Python 3.12+"
            exit 1
        fi

        # Check if virtual environment exists
        if [ ! -d "venv" ]; then
            echo "📦 Creating virtual environment..."
            python3 -m venv venv
        fi

        echo "📦 Activating virtual environment and installing dependencies..."
        source venv/bin/activate
        pip install -r requirements.txt

        echo "🚀 Starting Streamlit app..."
        echo "Make sure Ollama is running locally (ollama serve)"
        streamlit run streamlit_app.py
        ;;
    4)
        echo "📥 Setting up Ollama models..."

        # Start only Ollama if not running
        if ! docker ps | grep -q ollama; then
            echo "Starting Ollama container..."
            docker-compose -f docker-compose.simple.yml up -d ollama
            sleep 5
        fi

        echo "Pulling required models..."
        docker exec ollama ollama pull qwen2.5:7b
        docker exec ollama ollama pull deepseek-r1:14b

        echo "✅ Models downloaded successfully!"
        echo "Available models:"
        docker exec ollama ollama list
        ;;
    5)
        echo "🛑 Stopping all services..."
        docker-compose -f docker-compose.simple.yml down
        docker-compose -f docker-compose.full.yml down
        echo "✅ All services stopped!"
        ;;
    *)
        echo "❌ Invalid choice. Please run the script again."
        exit 1
        ;;
esac

echo
echo "🔗 Useful commands:"
echo "   View logs: docker-compose logs -f [service-name]"
echo "   Restart service: docker-compose restart [service-name]"
echo "   Stop services: docker-compose down"
echo "   Update app: docker-compose up -d --build chronology-agent"
