# Chronology Agent Deployment Guide

This guide provides multiple options to deploy your Chronology Agent application.

## 🚀 Quick Start

### Option 1: Simple Docker Deployment (Recommended)

1. **Clone and navigate to the project:**

   ```bash
   cd /Users/eslamelmishtawy/Desktop/Chronology_Agent
   ```

2. **Run the deployment script:**

   ```bash
   ./deploy.sh
   ```

   Choose option 1 for simple deployment.

3. **Download AI models:**

   ```bash
   ./deploy.sh
   ```

   Choose option 4 to download required models.

4. **Access the application:**
   - Chronology Agent: http://localhost:8501
   - Ollama API: http://localhost:11434

### Option 2: Manual Docker Commands

```bash
# Build and start services
docker-compose -f docker-compose.simple.yml up -d --build

# Download AI models
docker exec ollama ollama pull qwen2.5:7b
docker exec ollama ollama pull deepseek-r1:14b

# Check status
docker-compose -f docker-compose.simple.yml ps
```

## 📋 Deployment Options

### 1. Simple Deployment

- **File:** `docker-compose.simple.yml`
- **Services:** Chronology Agent + Ollama
- **Use case:** Basic deployment for document processing

### 2. Full Deployment with Monitoring

- **File:** `docker-compose.full.yml`
- **Services:** Chronology Agent + Ollama + Langfuse + PostgreSQL + Redis + ClickHouse + MinIO
- **Use case:** Production deployment with full monitoring and tracing

### 3. Local Development

- **Setup:** Python virtual environment
- **Use case:** Development and testing

## 🔧 Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Key settings to update:

- `LANGFUSE_*` - Langfuse monitoring credentials
- `OLLAMA_HOST` - Ollama server URL
- `SECRET_KEY` - Application secret key
- `OPENAI_API_KEY` - If using OpenAI instead of Ollama

### Security Considerations

**For Production Deployment:**

1. **Change default passwords** in docker-compose files:

   - PostgreSQL password
   - Redis password
   - MinIO credentials
   - ClickHouse password

2. **Generate secure keys:**

   ```bash
   # Generate encryption key
   openssl rand -hex 32

   # Generate secret keys
   openssl rand -base64 32
   ```

3. **Update environment variables** with generated keys

## 🐳 Docker Services

### Main Application

- **Port:** 8501
- **Health check:** `http://localhost:8501/_stcore/health`
- **Volumes:** `./uploads`, `./sample_documents`

### Ollama (AI Models)

- **Port:** 11434
- **Volume:** `ollama_data` (persistent model storage)
- **Supported models:** qwen2.5:7b, deepseek-r1:14b

### Langfuse (Monitoring) - Full deployment only

- **Port:** 3000
- **Dependencies:** PostgreSQL, Redis, ClickHouse, MinIO

## 🛠️ Management Commands

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f chronology-agent
```

### Restart Services

```bash
# Restart application
docker-compose restart chronology-agent

# Restart all
docker-compose restart
```

### Update Application

```bash
# Rebuild and update
docker-compose up -d --build chronology-agent
```

### Stop Services

```bash
# Stop all
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### Manage Ollama Models

```bash
# List downloaded models
docker exec ollama ollama list

# Download new model
docker exec ollama ollama pull <model-name>

# Remove model
docker exec ollama ollama rm <model-name>
```

## 🌐 Cloud Deployment Options

### 1. AWS/Azure/GCP with Docker

1. Set up a VM with Docker installed
2. Clone your repository
3. Run the deployment script
4. Configure firewall rules for ports 8501, 3000, 11434

### 2. Railway.app

1. Connect your GitHub repository
2. Add a `railway.toml` file:

   ```toml
   [build]
   builder = "dockerfile"

   [deploy]
   healthcheckPath = "/_stcore/health"
   healthcheckTimeout = 300
   restartPolicyType = "on_failure"

   [[deploy.environment]]
   name = "PORT"
   value = "8501"
   ```

### 3. Render.com

1. Connect your GitHub repository
2. Use Web Service with Docker
3. Set environment variables in dashboard

### 4. DigitalOcean App Platform

1. Create a new app from GitHub
2. Use Dockerfile deployment
3. Configure environment variables

## 📊 Monitoring and Debugging

### Health Checks

- **Application:** `curl http://localhost:8501/_stcore/health`
- **Ollama:** `curl http://localhost:11434/api/version`
- **Langfuse:** `curl http://localhost:3000/api/public/health`

### Performance Monitoring

- **Langfuse Dashboard:** http://localhost:3000 (full deployment)
- **Docker Stats:** `docker stats`
- **Resource Usage:** `docker system df`

### Troubleshooting

#### Common Issues:

1. **Models not loading:**

   ```bash
   # Check Ollama logs
   docker logs ollama

   # Restart Ollama
   docker-compose restart ollama
   ```

2. **Application connection errors:**

   ```bash
   # Check network connectivity
   docker network ls
   docker network inspect chronology_default
   ```

3. **Memory issues:**

   ```bash
   # Monitor resource usage
   docker stats

   # Increase Docker memory limit in Docker Desktop
   ```

## 📱 Usage

1. **Access the web interface:** http://localhost:8501
2. **Upload a PDF document** using the file uploader
3. **Select AI model** (qwen2.5:7b or deepseek-r1:14b)
4. **Click "Process Document"** to start analysis
5. **View results** in the tabs provided

## 🔄 Updates and Maintenance

### Update Application Code

```bash
git pull origin main
docker-compose up -d --build chronology-agent
```

### Backup Data

```bash
# Backup volumes
docker run --rm -v chronology_ollama_data:/data -v $(pwd):/backup alpine tar czf /backup/ollama_backup.tar.gz -C /data .

# Backup uploads
tar czf uploads_backup.tar.gz uploads/
```

### Restore Data

```bash
# Restore ollama models
docker run --rm -v chronology_ollama_data:/data -v $(pwd):/backup alpine tar xzf /backup/ollama_backup.tar.gz -C /data
```

## 🆘 Support

If you encounter issues:

1. Check the logs: `docker-compose logs -f`
2. Verify environment configuration
3. Ensure all required ports are available
4. Check Docker system resources
5. Review the troubleshooting section above

For additional help, check the application logs and Docker container status.
