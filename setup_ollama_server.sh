#!/bin/bash
# Quick Ollama Server Setup Script for Ubuntu/Debian

set -e

echo "🚀 Setting up Ollama Server..."

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install curl if not present
sudo apt install curl -y

# Install Ollama
echo "🤖 Installing Ollama..."
curl -fsSL https://ollama.ai/install.sh | sh

# Configure Ollama to listen on all interfaces
echo "⚙️ Configuring Ollama..."
sudo mkdir -p /etc/systemd/system/ollama.service.d
sudo tee /etc/systemd/system/ollama.service.d/override.conf > /dev/null << EOF
[Service]
Environment="OLLAMA_HOST=0.0.0.0:11434"
EOF

# Reload and restart
sudo systemctl daemon-reload
sudo systemctl restart ollama
sudo systemctl enable ollama

# Configure firewall
echo "🔒 Configuring firewall..."
sudo ufw allow 11434/tcp
sudo ufw --force enable

# Wait for Ollama to start
echo "⏳ Waiting for Ollama to start..."
sleep 10

# Pull models
echo "📥 Pulling AI models..."
ollama pull qwen2.5:7b
ollama pull deepseek-r1:14b

# Test installation
echo "🧪 Testing installation..."
curl http://localhost:11434/api/tags

echo "✅ Ollama server setup complete!"
echo ""
echo "🌐 Your Ollama server is running at:"
echo "   Local: http://localhost:11434"
echo "   External: http://$(curl -s ifconfig.me):11434"
echo ""
echo "📋 Next steps:"
echo "1. Note your server's public IP address"
echo "2. Update your Streamlit Cloud secrets with:"
echo "   OLLAMA_BASE_URL = \"http://YOUR-SERVER-IP:11434\""
echo "3. Deploy your Streamlit app"
echo ""
echo "🔍 Check server status with:"
echo "   systemctl status ollama"
echo "   journalctl -u ollama -f"
