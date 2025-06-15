# 🚂 Railway Ollama Deployment

Deploy Ollama with AI models to Railway cloud platform in minutes.

## 🚀 Quick Start

### Option 1: Automated Script

```bash
# Run the deployment script
./deploy-railway.sh
```

### Option 2: Manual Deployment

1. **Install Railway CLI:**

   ```bash
   # macOS
   brew install railway

   # Linux
   curl -fsSL https://railway.app/install.sh | sh
   ```

2. **Login to Railway:**

   ```bash
   railway login
   ```

3. **Create and deploy:**
   ```bash
   railway init
   railway up
   ```

## 📋 What Gets Deployed

- **Ollama server** running on Railway's infrastructure
- **Pre-installed models:**
  - `qwen2.5:7b` - General purpose AI model
  - `deepseek-r1:14b` - Advanced reasoning model
- **Health checks** and automatic restarts
- **HTTPS endpoint** with Railway domain

## 🔧 Configuration Files

- `Dockerfile.railway` - Container configuration
- `railway.toml` - Railway deployment settings
- `start-railway.sh` - Startup script with model downloading
- `deploy-railway.sh` - Automated deployment script

## 🌐 Using Your Deployed Ollama

Once deployed, update your Streamlit app configuration:

```python
# In your Python code
import os
OLLAMA_BASE_URL = "https://your-project-name.up.railway.app"

# Or in .streamlit/secrets.toml
OLLAMA_BASE_URL = "https://your-project-name.up.railway.app"
```

## 💰 Costs

- **Free Tier:** Good for testing (500 execution hours)
- **Pro Plan:** $20/month for production use

## 🔍 Monitoring

- View logs: `railway logs`
- Check status: `railway status`
- Open dashboard: `railway open`

## 🆘 Troubleshooting

**Issue:** Models not loading

```bash
# Check logs
railway logs --follow
```

**Issue:** Connection refused

- Ensure your Railway app is deployed and running
- Check the correct domain in your Streamlit configuration

**Issue:** Out of memory

- Upgrade to Railway Pro plan for more resources
- Consider using smaller models like `qwen2.5:3b`
