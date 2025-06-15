#!/bin/bash

# Railway startup script for Ollama
set -e

# Use Railway PORT if available, otherwise default to 11434
export OLLAMA_HOST=0.0.0.0:${PORT:-11434}

echo "🚀 Starting Ollama on $OLLAMA_HOST"
echo "📁 Models directory: $OLLAMA_MODELS"

# Start Ollama in background
ollama serve &
OLLAMA_PID=$!

# Function to check if Ollama is ready
check_ollama() {
    curl -s -f http://localhost:${PORT:-11434}/api/tags > /dev/null 2>&1
}

# Wait for Ollama to start (max 60 seconds)
echo "⏳ Waiting for Ollama to start..."
for i in {1..60}; do
    if check_ollama; then
        echo "✅ Ollama is ready!"
        break
    fi
    if [ $i -eq 60 ]; then
        echo "❌ Ollama failed to start within 60 seconds"
        exit 1
    fi
    sleep 1
done

# Check if models are already downloaded
if ollama list | grep -q "qwen2.5:7b"; then
    echo "✅ qwen2.5:7b already available"
else
    echo "📥 Pulling qwen2.5:7b model..."
    ollama pull qwen2.5:7b
    echo "✅ qwen2.5:7b downloaded successfully"
fi

if ollama list | grep -q "deepseek-r1:14b"; then
    echo "✅ deepseek-r1:14b already available"
else
    echo "📥 Pulling deepseek-r1:14b model..."
    ollama pull deepseek-r1:14b
    echo "✅ deepseek-r1:14b downloaded successfully"
fi

echo "🎉 All models ready! Server is now accepting requests."
echo "🔗 API endpoint: http://localhost:${PORT:-11434}"

# List available models
echo "📋 Available models:"
ollama list

# Keep the server running
wait $OLLAMA_PID
