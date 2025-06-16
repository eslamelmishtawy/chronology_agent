#!/usr/bin/env python3
"""
Streamlit interface for the Chronology Agent workflow.
Provides real-time progress tracking and file upload functionality.
Supports ChatGroq and local Ollama servers.
"""
import os
import tempfile
import time
import requests

import streamlit as st

from document_analyzer import document_analyzer_node
from document_formatter import document_formatter_node
from document_models import DocumentData, AgentState
from document_reader import document_reader_node
from reflection_agent import reflection_node


def get_groq_api_key():
    """Get Groq API key from secrets or environment variables."""
    # Try Streamlit secrets first
    if hasattr(st, 'secrets') and 'GROQ_API_KEY' in st.secrets:
        return st.secrets['GROQ_API_KEY']

    # Try environment variable
    return os.getenv('GROQ_API_KEY')


def get_ollama_base_url():
    """Get Ollama base URL from secrets or environment variables."""
    # Try Streamlit secrets first
    if hasattr(st, 'secrets') and 'OLLAMA_BASE_URL' in st.secrets:
        return st.secrets['OLLAMA_BASE_URL']

    # Try environment variable
    env_url = os.getenv('OLLAMA_BASE_URL')
    if env_url:
        return env_url

    # Default to local
    return "http://localhost:11434"


def test_ollama_connection(base_url: str) -> bool:
    """Test if Ollama server is accessible."""
    try:
        response = requests.get(f"{base_url}/api/tags", timeout=10)
        return response.status_code == 200
    except Exception:
        return False


def create_groq_client(model_name: str = "llama-3.1-70b-versatile"):
    """Create ChatGroq client."""
    try:
        from langchain_groq import ChatGroq
        api_key = get_groq_api_key()
        if not api_key:
            st.error("❌ GROQ_API_KEY not found in secrets or environment variables")
            return None

        return ChatGroq(
            groq_api_key=api_key,
            model_name=model_name,
            temperature=0,
            max_tokens=8192
        )
    except Exception as e:
        st.error(f"❌ Failed to initialize ChatGroq: {str(e)}")
        return None


def create_ollama_client(model_name: str, base_url: str):
    """Create ChatOllama client with custom base URL."""
    try:
        from langchain_ollama import ChatOllama
        return ChatOllama(
            model=model_name,
            temperature=0,
            num_ctx=16000,
            base_url=base_url,
        )
    except Exception as e:
        st.error(f"❌ Failed to initialize Ollama: {str(e)}")
        return None


def init_session_state():
    """Initialize session state variables."""
    if 'workflow_status' not in st.session_state:
        st.session_state.workflow_status = {}
    if 'result' not in st.session_state:
        st.session_state.result = None
    if 'processing' not in st.session_state:
        st.session_state.processing = False


def update_status(step: str, status: str, message: str = ""):
    """Update the status of a workflow step."""
    st.session_state.workflow_status[step] = {
        'status': status,  # 'pending', 'running', 'completed', 'error'
        'message': message,
        'timestamp': time.time()
    }


def display_status_card(step_name: str, step_key: str, description: str):
    """Display a status card for a workflow step."""
    if step_key not in st.session_state.workflow_status:
        status = 'pending'
        message = ""
        icon = "⏳"
        color = "gray"
    else:
        step_info = st.session_state.workflow_status[step_key]
        status = step_info['status']
        message = step_info['message']

        if status == 'pending':
            icon = "⏳"
            color = "gray"
        elif status == 'running':
            icon = "🔄"
            color = "blue"
        elif status == 'completed':
            icon = "✅"
            color = "green"
        elif status == 'error':
            icon = "❌"
            color = "red"
        else:
            icon = "❓"
            color = "gray"

    # Create status card
    with st.container():
        col1, col2 = st.columns([1, 10])
        with col1:
            st.markdown(f"<h2 style='color: {color}; margin: 0;'>{icon}</h2>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"**{step_name}**")
            st.caption(description)
            if message:
                if status == 'error':
                    st.error(message)
                elif status == 'completed':
                    st.success(message)
                else:
                    st.info(message)
        st.divider()


def run_chronology_workflow(file_path: str, progress_container, llm_provider: str = "groq", model_name: str = "llama-3.1-70b-versatile"):
    """Run the chronology workflow with real-time progress updates."""

    with progress_container.container():
        st.subheader("🔄 Workflow Progress")

        # Initialize all steps as pending
        steps = [
            ("reader", "📖 Document Reader", "Loading and extracting text from PDF"),
            ("analyzer", "🔍 Document Analyzer", "Analyzing content and extracting structured data"),
            ("reviewer", "🔍 Reflection Agent", "Reviewing data completeness and accuracy"),
            ("formatter", "📝 Document Formatter", "Formatting final chronology output")
        ]

        for step_key, step_name, description in steps:
            update_status(step_key, 'pending')

        # Display initial status
        status_placeholder = st.empty()

        try:
            # Create the agent graph
            update_status("reader", "running", "Initializing workflow...")
            with status_placeholder.container():
                for step_key, step_name, description in steps:
                    display_status_card(step_name, step_key, description)

            # Prepare initial state
            initial_state: AgentState = {
                "file_path": file_path,
                "pdf_content": "",
                "document_data": DocumentData(),
                "review_feedback": "",
                "formatted_output": "",
                "is_complete": False,
                "retry_count": 0
            }

            # Custom workflow execution with status updates
            state = initial_state.copy()

            # Step 1: Document Reader
            update_status("reader", "running", "Loading PDF document...")
            with status_placeholder.container():
                for step_key, step_name, description in steps:
                    display_status_card(step_name, step_key, description)
            time.sleep(1)  # Brief pause for UI update

            state = document_reader_node(state)

            if state.get("pdf_content"):
                char_count = len(state["pdf_content"])
                update_status("reader", "completed", f"Successfully loaded {char_count:,} characters")
            else:
                update_status("reader", "error", "Failed to load PDF content")
                return None

            # Step 2: Document Analyzer
            update_status("analyzer", "running", "Analyzing document with AI...")
            with status_placeholder.container():
                for step_key, step_name, description in steps:
                    display_status_card(step_name, step_key, description)
            time.sleep(1)

            # Create LLM for analysis
            try:
                if llm_provider == "groq":
                    llm = create_groq_client(model_name)
                    if llm is None:
                        st.error("❌ Failed to create ChatGroq client")
                        return None
                    st.info(f"🤖 Using ChatGroq model: {model_name}")
                else:
                    # Fallback to Ollama
                    base_url = get_ollama_base_url()
                    if not test_ollama_connection(base_url):
                        st.error(f"❌ Ollama server not reachable at {base_url}")
                        return None
                    llm = create_ollama_client(model_name, base_url)
                    if llm is None:
                        st.error("❌ Failed to create Ollama client")
                        return None
                    st.info(f"🤖 Using Ollama model: {model_name} at {base_url}")
            except Exception as e:
                st.error(f"❌ Failed to initialize LLM: {str(e)}")
                return None

            state = document_analyzer_node(state, llm)

            doc_data = state.get("document_data", DocumentData())
            if doc_data.document_type:
                update_status("analyzer", "completed", f"Extracted {doc_data.document_type} document data")
            else:
                update_status("analyzer", "error", "Failed to extract document data")

            # Step 3: Reflection Agent
            update_status("reviewer", "running", "Reviewing data quality...")
            with status_placeholder.container():
                for step_key, step_name, description in steps:
                    display_status_card(step_name, step_key, description)
            time.sleep(1)

            # Run reflection with retry logic
            max_retries = 2
            for attempt in range(max_retries + 1):
                state = reflection_node(state, llm)
                if state.get("is_complete", False):
                    break
                if attempt < max_retries:
                    update_status("reviewer", "running", f"Retry {attempt + 1}/{max_retries} - Re-analyzing...")
                    state = document_analyzer_node(state, llm)
                    with status_placeholder.container():
                        for step_key, step_name, description in steps:
                            display_status_card(step_name, step_key, description)
                    time.sleep(1)

            if state.get("is_complete", False):
                update_status("reviewer", "completed", "Data quality review passed")
            else:
                update_status("reviewer", "completed", "Completed with maximum retries")

            # Step 4: Document Formatter
            update_status("formatter", "running", "Formatting chronology output...")
            with status_placeholder.container():
                for step_key, step_name, description in steps:
                    display_status_card(step_name, step_key, description)
            time.sleep(1)

            state = document_formatter_node(state, llm)

            if state.get("formatted_output"):
                update_status("formatter", "completed", "Chronology formatted successfully")
            else:
                update_status("formatter", "error", "Failed to format output")

            # Final status update
            with status_placeholder.container():
                for step_key, step_name, description in steps:
                    display_status_card(step_name, step_key, description)

            return state

        except (ValueError, TypeError, AttributeError, KeyError) as e:
            # Update current step as error
            for step_key, _, _ in steps:
                if st.session_state.workflow_status.get(step_key, {}).get('status') == 'running':
                    update_status(step_key, "error", f"Error: {str(e)}")
                    break

            with status_placeholder.container():
                for step_key, step_name, description in steps:
                    display_status_card(step_name, step_key, description)

            st.error(f"Workflow failed: {str(e)}")
            return None



def main():
    """Main Streamlit application."""
    st.set_page_config(
        page_title="Chronology Agent",
        page_icon="📄",
        layout="wide"
    )

    init_session_state()

    # Header
    st.title("📄 Chronology Agent")
    st.markdown("Upload a PDF document to extract chronological information using AI agents.")
    st.divider()

    # File upload section
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📁 Upload Document")

        # LLM Provider selection
        st.subheader("🤖 AI Model Selection")

        # Check if Groq API key is available
        groq_api_key = get_groq_api_key()

        if groq_api_key:
            llm_provider = st.selectbox(
                "Choose AI Provider",
                options=["groq", "ollama"],
                index=0,  # Default to Groq
                format_func=lambda x: "ChatGroq (Recommended)" if x == "groq" else "Local Ollama",
                help="ChatGroq is faster and more reliable. Ollama requires local setup."
            )
        else:
            st.warning("⚠️ ChatGroq API key not found. Using Local Ollama only.")
            llm_provider = "ollama"

        # Model selection based on provider
        if llm_provider == "groq":
            selected_model = st.selectbox(
                "Choose ChatGroq Model",
                options=["meta-llama/llama-4-maverick-17b-128e-instruct", "llama-3.1-8b-instant", "mixtral-8x7b-32768"],
                index=0,  # Default to llama-3.1-70b-versatile
                help="Select the ChatGroq model for document analysis"
            )
            st.info(f"🚀 **ChatGroq**: Using model {selected_model}")
            st.caption("Fast, reliable cloud-based AI processing")

            # Test connection button for Groq
            if st.button("🔌 Test ChatGroq Connection"):
                with st.spinner("Testing ChatGroq connection..."):
                    test_llm = create_groq_client(selected_model)
                    if test_llm:
                        st.success("✅ Connected to ChatGroq successfully!")
                    else:
                        st.error("❌ Failed to connect to ChatGroq")
        else:
            selected_model = st.selectbox(
                "Choose Ollama Model",
                options=["qwen2.5:7b", "llama3.1:8b", "phi3:mini"],
                index=0,  # Default to qwen2.5:7b
                help="Select the local Ollama model for document analysis"
            )

            # Show Ollama server configuration
            base_url = get_ollama_base_url()
            st.info(f"🤖 **Local Ollama**: Using model {selected_model}")
            st.caption(f"Server: {base_url}")

            # Test connection button for Ollama
            if st.button("🔌 Test Ollama Connection"):
                with st.spinner("Testing Ollama connection..."):
                    if test_ollama_connection(base_url):
                        st.success(f"✅ Connected to Ollama server at {base_url}")
                    else:
                        st.error(f"❌ Cannot connect to Ollama server at {base_url}")
                        st.error("Make sure Ollama is running locally: `ollama serve`")

        uploaded_file = st.file_uploader(
            "Choose a PDF file",
            type="pdf",
            help="Upload a PDF document to process"
        )

        if uploaded_file is not None:
            st.success(f"✅ File uploaded: {uploaded_file.name}")
            st.info(f"📊 File size: {uploaded_file.size:,} bytes")

            # Process button
            if st.button("🚀 Process Document", type="primary", disabled=st.session_state.processing):
                st.session_state.processing = True
                st.session_state.workflow_status = {}
                st.session_state.result = None

                # Save uploaded file temporarily
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    temp_file_path = tmp_file.name

                try:
                    # Create progress container
                    progress_container = st.empty()

                    # Run workflow
                    result = run_chronology_workflow(temp_file_path, progress_container, llm_provider, selected_model)
                    st.session_state.result = result

                finally:
                    # Clean up temporary file
                    if os.path.exists(temp_file_path):
                        os.unlink(temp_file_path)
                    st.session_state.processing = False

    with col2:
        st.subheader("ℹ️ How it works")
        st.markdown("""
        The Chronology Agent uses **4 specialized AI agents**:

        1. **📖 Document Reader** - Extracts text from PDF
        2. **🔍 Document Analyzer** - Extracts structured data
        3. **🔍 Reflection Agent** - Reviews data quality
        4. **📝 Document Formatter** - Creates chronology entry

        **Supported Document Types:**
        - Letters, Emails, RFI, IR
        - Submittals, Transmittals, VO, SWI
        - Drawings and other project documents
        """)

        st.subheader("🚀 AI Providers")
        groq_api_key = get_groq_api_key()

        if groq_api_key:
            st.markdown("""
            **ChatGroq (Recommended):**
            - ⚡ Fast processing
            - 🌐 Cloud-based
            - 🎯 High accuracy
            - ✅ Ready to use
            """)

        st.markdown("""
        **Local Ollama Setup:**
        1. Install Ollama: `curl -fsSL https://ollama.ai/install.sh | sh`
        2. Start Ollama: `ollama serve`
        3. Pull model: `ollama pull qwen2.5:7b`

        **For Streamlit Cloud:**
        - Set `GROQ_API_KEY` in app secrets for ChatGroq
        - Or deploy local Ollama and set `OLLAMA_BASE_URL`
        """)

    # Results section
    if st.session_state.result:
        st.divider()
        st.subheader("📋 Results")

        result = st.session_state.result

        # Tabs for different views
        tab1, tab2, tab3 = st.tabs(["📄 Final Output", "📊 Extracted Data", "🔍 Review Feedback"])

        with tab1:
            st.subheader("🎯 Chronology Entry")
            formatted_output = result.get("formatted_output", "No output generated")
            if formatted_output != "No output generated":
                st.success("✅ Chronology entry generated successfully!")
                st.markdown("### Output:")
                st.markdown(formatted_output)

                # Download button
                st.download_button(
                    label="💾 Download Chronology Entry",
                    data=formatted_output,
                    file_name=f"chronology_{int(time.time())}.txt",
                    mime="text/plain"
                )
            else:
                st.error("❌ No output was generated")

        with tab2:
            st.subheader("📊 Extracted Information")
            doc_data = result.get("document_data", DocumentData())

            col1, col2 = st.columns(2)
            with col1:
                st.metric("Document Type", doc_data.document_type or "Not extracted")
                st.metric("Document Date", doc_data.document_date or "Not extracted")
                st.metric("Main Reference", doc_data.document_mainreference or "Not extracted")

            with col2:
                total_parties = len(doc_data.document_senderparty) + len(doc_data.document_recipientparty)
                st.metric("Number of Parties", total_parties)

            # Display sender parties
            if doc_data.document_senderparty:
                st.subheader("📤 Sender Parties")
                for i, party in enumerate(doc_data.document_senderparty, 1):
                    st.write(f"{i}. **{party.name}** - {party.role}")

            # Display recipient parties
            if doc_data.document_recipientparty:
                st.subheader("� Recipient Parties")
                for i, party in enumerate(doc_data.document_recipientparty, 1):
                    st.write(f"{i}. **{party.name}** - {party.role}")

            # Display other references if available
            if doc_data.document_otherreferences:
                st.subheader("🔗 Other References")
                for i, ref in enumerate(doc_data.document_otherreferences, 1):
                    st.write(f"{i}. {ref}")

            if doc_data.document_description:
                st.subheader("📝 Description")
                st.write(doc_data.document_description)

        with tab3:
            st.subheader("🔍 Quality Review")
            review_feedback = result.get("review_feedback", "No feedback available")
            st.markdown(review_feedback)

    # Footer
    st.divider()
    st.caption("Powered by ChatGroq & LangGraph • Built with Streamlit")


if __name__ == "__main__":
    main()
