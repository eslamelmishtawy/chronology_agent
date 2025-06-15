# 📄 Chronology Agent

A Streamlit application that uses AI agents to extract chronological information from PDF documents using local Ollama models. Perfect for legal, construction, and project management document analysis.

## 🚀 Quick Start

1. **Install Ollama:** Download from [ollama.ai](https://ollama.ai)
2. **Pull a model:** `ollama pull qwen2.5:7b`
3. **Install dependencies:** `pip install -r requirements.txt`
4. **Run the app:** `streamlit run streamlit_app.py`

## ✨ Features

- **📖 Document Reader** - Extracts text from PDF documents
- **🔍 Document Analyzer** - Uses local AI to extract structured data
- **🔍 Reflection Agent** - Reviews and validates extracted information
- **📝 Document Formatter** - Creates formatted chronology entries

## 📋 Supported Document Types

- Letters, Emails, RFI, IR
- Submittals, Transmittals, VO, SWI
- Meeting minutes, notices, claims
- Technical drawings and specifications
- Any construction/project management documents

## 🛠️ Technology Stack

- **Frontend:** Streamlit
- **AI Models:** Local Ollama (qwen2.5:7b, deepseek-r1:14b)
- **Document Processing:** LangChain, PyPDF
- **Privacy:** 100% local processing - no data sent to external APIs

## 🔧 Local Setup

1. **Install Ollama:**

   ```bash
   # macOS
   brew install ollama

   # Or download from https://ollama.ai
   ```

2. **Start Ollama and pull models:**

   ```bash
   ollama serve  # Start Ollama service
   ollama pull qwen2.5:7b  # Default model
   ollama pull deepseek-r1:14b  # Alternative model
   ```

3. **Clone and install dependencies:**

   ```bash
   git clone https://github.com/yourusername/chronology-agent.git
   cd chronology-agent
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   streamlit run streamlit_app.py
   ```

## 🌐 Deployment

### Local Development

This application runs locally with Ollama:

1. Make sure Ollama is running: `ollama serve`
2. Pull required models: `ollama pull qwen2.5:7b`
3. Run the app: `streamlit run streamlit_app.py`

### Streamlit Cloud Deployment

To deploy on Streamlit Cloud, you need to set up a remote Ollama server:

#### Option 1: Quick Setup with DigitalOcean

1. **Create a DigitalOcean Droplet** (4GB+ RAM recommended)
2. **Run the setup script:**

   ```bash
   # Copy setup script to your server
   scp setup_ollama_server.sh root@your-server-ip:~/

   # SSH into server and run setup
   ssh root@your-server-ip
   chmod +x setup_ollama_server.sh
   ./setup_ollama_server.sh
   ```

3. **Configure Streamlit Cloud:**
   - Go to your Streamlit Cloud app settings
   - Add secret: `OLLAMA_BASE_URL = "http://YOUR-SERVER-IP:11434"`
   - Deploy your app

#### Option 2: Other Cloud Providers

See `OLLAMA_DEPLOYMENT_GUIDE.md` for detailed instructions on:

- Railway deployment
- Render deployment
- AWS/GCP setup

### Environment Configuration

The app automatically detects your Ollama server:

- **Local:** Uses `http://localhost:11434` by default
- **Remote:** Set `OLLAMA_BASE_URL` environment variable or Streamlit secret

## 📄 Usage

1. **Make sure Ollama is running** with your preferred model
2. **Upload a PDF document** using the file uploader
3. **Select your AI model** from the dropdown (qwen2.5:7b or deepseek-r1:14b)
4. **Click "Process Document"** to start the AI analysis
5. **Review the results** in the generated tabs:
   - **Final Output:** Formatted chronology entry
   - **Extracted Data:** Structured information
   - **Review Feedback:** Quality assessment

## 🤖 Supported Models

- **qwen2.5:7b** - Fast and efficient, good for most documents
- **deepseek-r1:14b** - More powerful, better for complex documents
- Add more models by installing them with `ollama pull model_name`

## 📊 Sample Output

```
On 25 December 2024, Contractor sent letter to the Project Owner requesting confirmation on architectural design options, including three design alternatives with completed cost comparisons against the Preliminary Technical Specification signed in April 2020, via letter Letter-CA-EA-0240.
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📝 License

This project is licensed under the MIT License.

## 🆘 Support

If you encounter any issues:

1. Make sure Ollama is running: `ollama serve`
2. Check that your model is available: `ollama list`
3. Ensure your PDF is text-based (not scanned images)
4. Try with a smaller PDF if you get memory errors

## 📊 System Requirements

- **RAM:** 8GB minimum (16GB recommended for larger models)
- **Storage:** 5-10GB for models
- **OS:** macOS, Linux, or Windows with WSL2

---

**Built with ❤️ using Streamlit and Ollama for 100% local AI processing**
