@echo off
REM Windows deployment script for Chronology Agent

echo 🚀 Chronology Agent Deployment Script (Windows)
echo ==========================================

REM Create necessary directories
if not exist "uploads" mkdir uploads

REM Copy environment file if it doesn't exist
if not exist ".env" (
    echo 📄 Creating .env file from template...
    copy .env.example .env
    echo ⚠️  Please edit .env file with your configuration before proceeding!
    echo    Key settings to update:
    echo    - Change default passwords
    echo    - Set your OpenAI API key if using OpenAI
    echo    - Configure Langfuse settings
    pause
)

echo.
echo Choose deployment option:
echo 1^) Simple ^(App + Ollama only^)
echo 2^) Full ^(App + Ollama + Langfuse monitoring^)
echo 3^) Pull and setup Ollama models
echo 4^) Stop all services
echo.

set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" (
    echo 🐳 Starting simple deployment...
    docker-compose -f docker-compose.simple.yml up -d --build
    echo ✅ Services started!
    echo 📱 Chronology Agent: http://localhost:8501
    echo 🤖 Ollama API: http://localhost:11434
)

if "%choice%"=="2" (
    echo 🐳 Starting full deployment with monitoring...
    docker-compose -f docker-compose.full.yml up -d --build
    echo ✅ Services started!
    echo 📱 Chronology Agent: http://localhost:8501
    echo 🤖 Ollama API: http://localhost:11434
    echo 📊 Langfuse Dashboard: http://localhost:3000
    echo 💾 MinIO Console: http://localhost:9091
)

if "%choice%"=="3" (
    echo 📥 Setting up Ollama models...
    docker-compose -f docker-compose.simple.yml up -d ollama
    timeout /t 5 /nobreak >nul
    echo Pulling required models...
    docker exec ollama ollama pull qwen2.5:7b
    docker exec ollama ollama pull deepseek-r1:14b
    echo ✅ Models downloaded successfully!
    docker exec ollama ollama list
)

if "%choice%"=="4" (
    echo 🛑 Stopping all services...
    docker-compose -f docker-compose.simple.yml down
    docker-compose -f docker-compose.full.yml down
    echo ✅ All services stopped!
)

echo.
echo 🔗 Useful commands:
echo    View logs: docker-compose logs -f [service-name]
echo    Restart service: docker-compose restart [service-name]
echo    Stop services: docker-compose down
echo    Update app: docker-compose up -d --build chronology-agent

pause
