from langchain_community.document_loaders import PyPDFLoader
from langchain_core.tools import tool

from document_models import AgentState, DocumentData
from langfuse_config import trace_tool_call, trace_workflow_step, langfuse_config


@tool
@trace_tool_call("load_pdf_document")
def load_pdf_document(file_path: str) -> str:
    """Load and extract text content from a PDF document."""
    trace = None
    try:
        # Create trace for PDF loading operation
        trace = langfuse_config.create_trace(
            name="pdf_document_loading",
            metadata={
                "file_path": file_path,
                "operation": "load_pdf_document"
            }
        )

        loader = PyPDFLoader(file_path, mode="single")
        docs = loader.load()

        content = docs[0].page_content if docs else ""

        # Log successful loading
        if trace:
            trace.update(
                output={"content_length": len(content), "status": "success"},
                metadata={"pages_loaded": len(docs)}
            )

        return content

    except FileNotFoundError as e:
        error_msg = f"PDF file not found: {str(e)}"
        if trace:
            trace.update(level="ERROR", status_message=error_msg)
        return f"Error loading PDF: {error_msg}"
    except PermissionError as e:
        error_msg = f"Permission denied accessing PDF: {str(e)}"
        if trace:
            trace.update(level="ERROR", status_message=error_msg)
        return f"Error loading PDF: {error_msg}"
    except (ImportError, ValueError, OSError) as e:
        # Handle PDF parsing errors, dependency issues, and file system errors
        error_msg = f"Error processing PDF: {str(e)}"
        if trace:
            trace.update(level="ERROR", status_message=error_msg)
        return f"Error loading PDF: {error_msg}"


@trace_workflow_step("document_reader")
def document_reader_node(state: AgentState) -> AgentState:
    """Read document and extract raw content."""
    file_path = state.get("file_path", "")

    # Create main trace for document reading workflow
    main_trace = langfuse_config.create_trace(
        name="document_reader_workflow",
        metadata={
            "workflow_step": "document_reader",
            "file_path": file_path,
            "input_state_keys": list(state.keys())
        }
    )

    if not file_path:
        error_msg = "No file path provided"
        main_trace.update(
            level="WARNING",
            status_message=error_msg,
            output={"is_complete": False, "error": error_msg}
        )
        print(f"⚠️ {error_msg}")
        return {**state, "pdf_content": "", "is_complete": False}

    # Use the tool to load PDF content
    print(f"📖 Loading PDF from: {file_path}")
    pdf_content = load_pdf_document.invoke({"file_path": file_path})

    # Check if content was successfully loaded
    is_error = pdf_content.startswith("Error loading PDF:")
    content_length = len(pdf_content) if not is_error else 0

    if is_error:
        main_trace.update(
            level="ERROR",
            status_message=pdf_content,
            output={
                "is_complete": False,
                "error": pdf_content,
                "content_length": 0
            }
        )
        print(f"❌ {pdf_content}")
    else:
        main_trace.update(
            output={
                "is_complete": False,
                "content": pdf_content,
                "content_length": content_length,
                "agent_state": state,
                "status": "success"
            }
        )
        print(f"📖 Loaded PDF: {content_length} characters")

    # Flush traces to ensure they're sent to Langfuse
    langfuse_config.flush()

    return {
        **state,
        "pdf_content": pdf_content,
        "document_data": DocumentData(),
        "is_complete": False,
        "retry_count": 0
    }
