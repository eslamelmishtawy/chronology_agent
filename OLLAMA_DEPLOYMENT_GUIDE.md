# 🚀 Ollama Cloud Deployment Guide

This guide shows you how to deploy Ollama on a cloud server so your Streamlit Cloud app can access it.

## 🌐 Option 1: Deploy on DigitalOcean Droplet

### Step 1: Create a DigitalOcean Droplet

1. **Sign up for DigitalOcean** (or use AWS/GCP)
2. **Create a new Droplet:**
   - **Image:** Ubuntu 22.04 LTS
   - **Size:** 4GB RAM minimum (8GB+ recommended for larger models)
   - **Datacenter:** Choose closest to your users
   - **Authentication:** SSH keys or password

### Step 2: Install Ollama on the Server

```bash
# SSH into your server
ssh root@your-server-ip

# Update system
apt update && apt upgrade -y

# Install curl if not present
apt install curl -y

# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama service
systemctl start ollama
systemctl enable ollama

# Configure Ollama to listen on all interfaces
mkdir -p /etc/systemd/system/ollama.service.d
cat > /etc/systemd/system/ollama.service.d/override.conf << EOF
[Service]
Environment="OLLAMA_HOST=0.0.0.0:11434"
EOF

# Reload and restart
systemctl daemon-reload
systemctl restart ollama

# Pull your models
ollama pull qwen2.5:7b
ollama pull deepseek-r1:14b
```

### Step 3: Configure Firewall

```bash
# Allow Ollama port
ufw allow 11434/tcp

# Enable firewall
ufw --force enable

# Check status
ufw status
```

### Step 4: Test the Installation

```bash
# Test locally on server
curl http://localhost:11434/api/tags

# Test from your local machine
curl http://YOUR-SERVER-IP:11434/api/tags
```

## 🔧 Option 2: Deploy on Railway

Railway provides an easier deployment option with automatic HTTPS and domain management:

### Step 1: Create Railway Account

1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Verify your email and complete setup

### Step 2: Deploy Ollama

#### Method A: Using Railway Template (Recommended)

1. **Visit Railway Ollama Template:**

   - Go to: `https://railway.app/template/ollama`
   - Or search for "Ollama" in Railway templates

2. **Deploy Template:**
   - Click "Deploy Now"
   - Connect your GitHub account if not already connected
   - Choose repository name (e.g., `ollama-server`)
   - Click "Deploy"

#### Method B: Manual Deployment

1. **Create New Project:**

   - Click "New Project" in Railway dashboard
   - Select "Deploy from GitHub repo"
   - Create a new repository or use existing one

2. **Create Dockerfile:**

```dockerfile
FROM ollama/ollama:latest

# Install necessary packages
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV OLLAMA_HOST=0.0.0.0
ENV PORT=11434

# Expose port
EXPOSE $PORT

# Create startup script that handles Railway's dynamic port
RUN echo '#!/bin/bash\n\
# Use Railway PORT if available, otherwise default to 11434\n\
export OLLAMA_HOST=0.0.0.0:${PORT:-11434}\n\
echo "Starting Ollama on $OLLAMA_HOST"\n\
ollama serve &\n\
OLLAMA_PID=$!\n\
\n\
# Wait for Ollama to start\n\
echo "Waiting for Ollama to start..."\n\
sleep 15\n\
\n\
# Pull models\n\
echo "Pulling qwen2.5:7b model..."\n\
ollama pull qwen2.5:7b\n\
echo "Pulling deepseek-r1:14b model..."\n\
ollama pull deepseek-r1:14b\n\
\n\
echo "Models pulled successfully. Server ready."\n\
wait $OLLAMA_PID\n\
' > /start.sh && chmod +x /start.sh

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:${PORT:-11434}/api/tags || exit 1

CMD ["/start.sh"]
```

3. **Add railway.toml (Optional):**

```toml
[build]
builder = "dockerfile"

[deploy]
healthcheckPath = "/api/tags"
healthcheckTimeout = 300
restartPolicyType = "always"
```

### Step 3: Configure Environment Variables

1. **In Railway Dashboard:**
   - Go to your project
   - Click on "Variables" tab
   - Add these variables:
     ```
     OLLAMA_HOST=0.0.0.0
     OLLAMA_ORIGINS=*
     ```

### Step 4: Monitor Deployment

1. **Check Deployment Logs:**

   - Click on "Deployments" tab
   - View real-time logs during deployment
   - Wait for models to download (may take 10-15 minutes)

2. **Get Your Railway URL:**
   - Once deployed, Railway will provide a public URL
   - Format: `https://your-project-name.up.railway.app`

### Step 5: Test the Deployment

```bash
# Test the API endpoint
curl https://your-project-name.up.railway.app/api/tags

# Test model availability
curl https://your-project-name.up.railway.app/api/tags | jq '.models[].name'
```

### Railway-Specific Configuration

#### Resource Limits

- **Memory:** 8GB maximum on Pro plan
- **CPU:** Shared CPU cores
- **Storage:** 100GB included
- **Bandwidth:** Unlimited

#### Scaling Options

```toml
# railway.toml
[deploy]
replicas = 1  # Ollama doesn't support horizontal scaling
```

#### Custom Domain (Optional)

1. Go to project settings
2. Click "Domains"
3. Add your custom domain
4. Configure DNS as instructed

## 🛠️ Option 3: Use Render

### Step 1: Create Render Account

1. Go to [render.com](https://render.com)
2. Sign up with GitHub

### Step 2: Deploy Service

1. **Create Web Service**
2. **Use Docker:**

```dockerfile
FROM ollama/ollama:latest

ENV OLLAMA_HOST=0.0.0.0:$PORT

EXPOSE $PORT

RUN echo '#!/bin/bash\n\
export OLLAMA_HOST=0.0.0.0:$PORT\n\
ollama serve &\n\
sleep 15\n\
ollama pull qwen2.5:7b\n\
wait' > /start.sh && chmod +x /start.sh

CMD ["/start.sh"]
```

## ⚙️ Update Your Streamlit App

Once you have Ollama deployed, update your Streamlit app to use the remote server:

### For Railway Deployment:

1. **Set the Ollama URL** in Streamlit secrets:

   ```toml
   # .streamlit/secrets.toml
   OLLAMA_BASE_URL = "https://your-project-name.up.railway.app"
   ```

2. **Or use environment variable in Streamlit Cloud:**

   ```bash
   # In Streamlit Cloud app settings
   OLLAMA_BASE_URL="https://your-project-name.up.railway.app"
   ```

3. **Update your Python code:**

   ```python
   import os
   import streamlit as st

   # Get Ollama URL from environment or secrets
   ollama_url = os.getenv("OLLAMA_BASE_URL") or st.secrets.get("OLLAMA_BASE_URL", "http://localhost:11434")

   # Use with your LLM client
   from langchain_community.llms import Ollama
   llm = Ollama(base_url=ollama_url, model="qwen2.5:7b")
   ```

### For Other Deployments:

1. **DigitalOcean/VPS:**

   ```toml
   # .streamlit/secrets.toml
   OLLAMA_BASE_URL = "http://your-server-ip:11434"
   ```

2. **With Custom Domain:**
   ```toml
   # .streamlit/secrets.toml
   OLLAMA_BASE_URL = "https://your-domain.com"
   ```

## 💰 Cost Estimates

### Railway

- **Free Tier:** $0/month
  - 500 execution hours
  - 1GB RAM, 1 vCPU
  - Good for testing only
- **Pro Plan:** $20/month
  - 8GB RAM, 8 vCPU
  - Unlimited execution hours
  - Custom domains
  - **Recommended for production**

### DigitalOcean

- **4GB Droplet:** $24/month
- **8GB Droplet:** $48/month
- **16GB Droplet:** $96/month

### Render

- **Free tier:** 750 hours/month (limited resources)
- **Starter:** $7/month (512MB RAM - insufficient for most models)
- **Standard:** $25/month (2GB RAM)
- **Pro:** $85/month (8GB RAM - recommended)

## 🔒 Security Considerations

1. **Use HTTPS** with a reverse proxy (nginx + Let's Encrypt)
2. **Restrict access** to your Streamlit app only
3. **Use VPN** for additional security
4. **Monitor usage** to prevent abuse

## 📋 Next Steps

1. Choose your deployment method
2. Deploy Ollama server
3. Update your Streamlit app configuration
4. Test the connection
5. Deploy to Streamlit Cloud

## 🆘 Troubleshooting

### Common Issues:

- **Connection refused:** Check firewall settings
- **Models not loading:** Ensure sufficient RAM
- **Slow responses:** Consider upgrading server specs
- **Out of memory:** Use smaller models or more RAM

### Logs:

```bash
# Check Ollama logs
journalctl -u ollama -f

# Check if service is running
systemctl status ollama
```
