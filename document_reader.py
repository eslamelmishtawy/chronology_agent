from langchain_community.document_loaders import PyPDFLoader
from langchain_core.tools import tool

from document_models import AgentState, DocumentData


@tool
def load_pdf_document(file_path: str) -> str:
    """Load and extract text content from a PDF document."""
    try:
        loader = PyPDFLoader(file_path, mode="single")
        docs = loader.load()
        content = docs[0].page_content if docs else ""
        return content

    except FileNotFoundError as e:
        error_msg = f"PDF file not found: {str(e)}"
        return f"Error loading PDF: {error_msg}"
    except PermissionError as e:
        error_msg = f"Permission denied accessing PDF: {str(e)}"
        return f"Error loading PDF: {error_msg}"
    except (ImportError, ValueError, OSError) as e:
        # Handle PDF parsing errors, dependency issues, and file system errors
        error_msg = f"Error processing PDF: {str(e)}"
        return f"Error loading PDF: {error_msg}"


def document_reader_node(state: AgentState) -> AgentState:
    """Read document and extract raw content."""
    file_path = state.get("file_path", "")

    if not file_path:
        error_msg = "No file path provided"
        print(f"⚠️ {error_msg}")
        return {**state, "pdf_content": "", "is_complete": False}

    # Use the tool to load PDF content
    print(f"📖 Loading PDF from: {file_path}")
    pdf_content = load_pdf_document.invoke({"file_path": file_path})

    # Check if content was successfully loaded
    is_error = pdf_content.startswith("Error loading PDF:")
    content_length = len(pdf_content) if not is_error else 0

    if is_error:
        print(f"❌ {pdf_content}")
    else:
        print(f"📖 Loaded PDF: {content_length} characters")

    return {
        **state,
        "pdf_content": pdf_content,
        "document_data": DocumentData(),
        "is_complete": False,
        "retry_count": 0
    }
