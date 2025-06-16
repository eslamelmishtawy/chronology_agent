# Chronology Agent

An intelligent document processing system that extracts chronological information from PDF documents using AI agents. The system supports both **ChatGroq** (cloud-based) and **local Ollama** for AI processing.

## Features

- 📄 **PDF Document Processing**: Extract text and analyze content
- 🤖 **Multiple AI Providers**: ChatGroq (recommended) and local Ollama support
- 🔍 **Intelligent Analysis**: 4-stage AI workflow for comprehensive document analysis
- 📋 **Structured Output**: Generate formal chronological entries for legal documentation
- 🌐 **Web Interface**: User-friendly Streamlit interface

## AI Workflow

The system uses 4 specialized AI agents:

1. **📖 Document Reader** - Extracts text from PDF documents
2. **🔍 Document Analyzer** - Analyzes content and extracts structured data
3. **🔍 Reflection Agent** - Reviews data completeness and accuracy
4. **📝 Document Formatter** - Formats final chronology output

## Setup

### Prerequisites

- Python 3.8+
- pip

### Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd Chronology_Agent
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

### Configuration

#### Option 1: ChatGroq (Recommended)

1. Create `.streamlit/secrets.toml` file:

```toml
GROQ_API_KEY = "your_groq_api_key_here"
```

2. Or set environment variable:

```bash
export GROQ_API_KEY="your_groq_api_key_here"
```

#### Option 2: Local Ollama

1. Install Ollama:

```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

2. Start Ollama server:

```bash
ollama serve
```

3. Pull a model:

```bash
ollama pull qwen2.5:7b
```

4. Configure base URL in `.streamlit/secrets.toml`:

```toml
OLLAMA_BASE_URL = "http://localhost:11434"
```

## Usage

### Run the Application

```bash
streamlit run streamlit_app.py
```

### Using the Interface

1. **Choose AI Provider**: Select between ChatGroq or local Ollama
2. **Select Model**: Choose from available models
3. **Upload PDF**: Upload your document for processing
4. **Process**: Click "Process Document" to start analysis
5. **Review Results**: View extracted data and formatted chronology

### Supported Document Types

- Letters and Emails
- RFI (Request for Information)
- IR (Information Request)
- Submittals and Transmittals
- VO (Variation Orders)
- SWI (Site Work Instructions)
- Technical Drawings
- Project Reports

## API Keys

### ChatGroq

Get your API key from [Groq Console](https://console.groq.com/keys) and add it to your secrets configuration.

### Models Available

**ChatGroq Models:**

- `llama-3.1-70b-versatile` (recommended)
- `llama-3.1-8b-instant`
- `mixtral-8x7b-32768`

**Ollama Models:**

- `qwen2.5:7b` (recommended)
- `llama3.1:8b`
- `phi3:mini`

## Deployment

### Streamlit Cloud

1. Deploy to Streamlit Cloud
2. Add secrets in app settings:
   - `GROQ_API_KEY` for ChatGroq
   - `OLLAMA_BASE_URL` if using remote Ollama

### Local Development

1. Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml`
2. Add your API keys and configuration
3. Run `streamlit run streamlit_app.py`

## File Structure

```
├── streamlit_app.py          # Main Streamlit application
├── document_reader.py        # PDF text extraction
├── document_analyzer.py      # AI-powered document analysis
├── reflection_agent.py       # Quality review and validation
├── document_formatter.py     # Output formatting
├── document_models.py        # Data models and schemas
├── requirements.txt          # Python dependencies
├── .streamlit/
│   └── secrets.toml         # Configuration secrets
└── sample_documents/        # Example PDF files
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
