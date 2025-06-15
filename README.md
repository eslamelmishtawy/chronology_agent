# 📄 Chronology Agent

A Streamlit application that uses AI agents to extract chronological information from PDF documents. Perfect for legal, construction, and project management document analysis.

## 🚀 Live Demo

**Deployed on Streamlit Cloud:** [Your App URL Here]

## ✨ Features

- **📖 Document Reader** - Extracts text from PDF documents
- **🔍 Document Analyzer** - Uses AI to extract structured data
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
- **AI Model:** OpenAI GPT-4o-mini
- **Document Processing:** LangChain, PyPDF
- **Monitoring:** Langfuse (optional)

## 🔧 Local Development

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/chronology-agent.git
   cd chronology-agent
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   ```bash
   export OPENAI_API_KEY="your-openai-api-key"
   ```

4. **Run the application:**
   ```bash
   streamlit run streamlit_app.py
   ```

## 🌐 Deployment

This application is optimized for **Streamlit Cloud** deployment:

1. Fork this repository
2. Connect it to [Streamlit Cloud](https://share.streamlit.io)
3. Add your `OPENAI_API_KEY` to the secrets
4. Deploy!

## 📄 Usage

1. **Upload a PDF document** using the file uploader
2. **Click "Process Document"** to start the AI analysis
3. **Review the results** in the generated tabs:
   - **Final Output:** Formatted chronology entry
   - **Extracted Data:** Structured information
   - **Review Feedback:** Quality assessment

## 🔑 API Keys

You'll need an OpenAI API key from [platform.openai.com](https://platform.openai.com). The app uses GPT-4o-mini which is cost-effective (~$0.10-1.00 per document).

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
1. Check that your OpenAI API key is properly configured
2. Ensure your PDF is text-based (not scanned images)
3. Try with a smaller PDF if you get timeout errors

---

**Built with ❤️ using Streamlit and OpenAI**
