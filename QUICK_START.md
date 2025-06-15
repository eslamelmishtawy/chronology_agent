# 🚀 Quick Deployment Guide

## Option 1: Local Docker (Easiest - Start Here!)

```bash
# 1. Start the deployment
./deploy.sh

# 2. Choose option 1 (Simple deployment)
# 3. Choose option 4 (Download models)
# 4. Open http://localhost:8501
```

**That's it!** Your app is running locally.

---

## Option 2: Railway.app (Easiest Cloud)

### Step 1: Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/yourusername/chronology-agent.git
git push -u origin main
```

### Step 2: Deploy to Railway

1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repository
5. Railway will automatically deploy using your `Dockerfile.railway`

### Step 3: Add Environment Variables

In Railway dashboard, add:

- `OPENAI_API_KEY` = your OpenAI API key

**Cost:** ~$5-10/month

---

## Option 3: DigitalOcean (Best for Production)

### Step 1: Create Droplet

1. Go to [digitalocean.com](https://digitalocean.com)
2. Create account
3. Create Droplet: Ubuntu 22.04, 4GB RAM ($24/month)

### Step 2: Setup Server

```bash
# SSH into your droplet
ssh root@your-droplet-ip

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Clone your repo
git clone https://github.com/yourusername/chronology-agent.git
cd chronology-agent

# Deploy
./deploy.sh
# Choose option 1, then option 4
```

### Step 3: Access Your App

- Your app: `http://your-droplet-ip:8501`
- Secure with domain + SSL using nginx

---

## Option 4: Local Development (No Docker)

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Mac/Linux
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Install and start Ollama (separate terminal)
# Mac: brew install ollama && ollama serve
# Linux: curl -fsSL https://ollama.ai/install.sh | sh && ollama serve

# Download models
ollama pull qwen2.5:7b
ollama pull deepseek-r1:14b

# Run app
streamlit run streamlit_app.py
```

---

## 💡 Which Should You Choose?

**Just want to test?** → Option 1 (Local Docker)
**Want to share with others?** → Option 2 (Railway)
**Need production deployment?** → Option 3 (DigitalOcean)
**Want to develop/modify?** → Option 4 (Local Development)

## 🆘 Need Help?

1. **Local Docker issues:** Check if Docker is running
2. **Railway deployment fails:** Check Dockerfile.railway and logs
3. **DigitalOcean issues:** Ensure ports 8501 is open in firewall
4. **Models not working:** Try OpenAI API key instead of local models

## 🔑 OpenAI Setup (Optional but Recommended for Cloud)

1. Get API key from [platform.openai.com](https://platform.openai.com)
2. Add to your environment:
   ```bash
   export OPENAI_API_KEY="sk-your-key-here"
   ```
3. The app will automatically use OpenAI instead of local models

**Cost:** ~$0.10-1.00 per document (much cheaper than server costs)
