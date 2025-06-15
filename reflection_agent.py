from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool

from document_models import AgentState, DocumentData

REVIEW_PROMPT = '''
You are a comprehensive quality assurance agent specializing in legal document analysis. Your role is to ensure NO information is missed and ALL data is completely extracted.

Perform an exhaustive review of the extracted document data against the original document:

COMPLETENESS CHECK:
1. document_type - Must be specific and accurate (letter, email, RFI, IR, submittal, transmittal, VO, SWI, drawing, notice, claim, etc.)
2. document_date - Must be in YYYY-MM-DD format and correctly extracted
3. document_description - Must be COMPREHENSIVE, following the document's chronological order, and include ALL details, context, purpose, requests, decisions, implications
4. document_senderparty - Must include EVERY sending organization, individual, role, title mentioned in the document
5. document_recipientparty - Must include EVERY receiving organization, individual, role, title mentioned in the document
6. document_mainreference - Must include the primary/main reference number, code, or identifier for the document
7. document_otherreferences - Must include ALL other reference numbers, codes, project numbers, file numbers, version numbers mentioned

THOROUGH ANALYSIS REQUIRED:
- Scan for missed information in headers, footers, signatures, metadata
- Check for implied or referenced information not captured
- Verify all dates, deadlines, and time references are extracted
- Ensure all communication patterns and responses are noted
- Validate technical details, specifications, and requirements are included
- Confirm cost, time, and resource implications are captured
- Verify all sender parties (organizations/individuals sending the document) are identified with detailed roles
- Verify all recipient parties (organizations/individuals receiving the document) are identified with detailed roles
- Ensure the document description maintains chronological order as it appears in the original document
- Confirm all main and other reference numbers/codes are captured separately

REVIEW PROCESS:
1. Compare extracted data line-by-line with original document
2. Identify any missing information, no matter how small
3. Check for incomplete descriptions or summaries that need expansion and ensure chronological order is maintained
4. Verify all sender parties and recipient parties mentioned anywhere in the document are properly categorized
5. Ensure the main reference and all other references/codes are captured
6. Validate that the description follows the document's natural order and flow

If ANY information is missing, incomplete, or could be more detailed, provide specific feedback on what needs to be added or improved.

If the extraction is truly comprehensive and complete with NO missing information, respond with "COMPLETE".

Be extremely thorough - it is better to request more detail than to miss important information.
'''


@tool
def review_extracted_data(document_data: DocumentData, pdf_content: str, llm) -> str:
    """Review extracted data for completeness and accuracy."""

    # Create detailed data summary for thorough review

    # Create sender party details with name and role
    sender_parties_details = []
    for party in document_data.document_senderparty:
        sender_parties_details.append(f"{party.name} ({party.role})")

    # Create recipient party details with name and role
    recipient_parties_details = []
    for party in document_data.document_recipientparty:
        recipient_parties_details.append(f"{party.name} ({party.role})")

    # Format other references
    other_refs = ', '.join(document_data.document_otherreferences) if document_data.document_otherreferences else 'None'

    data_summary = f"""
    EXTRACTED DATA SUMMARY:

    Document Type: {document_data.document_type}
    Document Date: {document_data.document_date}
    Document Description: {document_data.document_description}

    Document Sender Parties ({len(document_data.document_senderparty)} found): {', '.join(sender_parties_details) if sender_parties_details else 'None'}

    Document Recipient Parties ({len(document_data.document_recipientparty)} found): {', '.join(recipient_parties_details) if recipient_parties_details else 'None'}

    Document Main Reference: {document_data.document_mainreference}

    Document Other References: {other_refs}

    Please perform a comprehensive review to ensure ALL information from the original document has been captured.
    """

    messages = [
        SystemMessage(content=REVIEW_PROMPT),
        HumanMessage(content=f"ORIGINAL DOCUMENT:\n{pdf_content}\n\n{data_summary}")
    ]

    try:
        response = llm.invoke(messages)
        return response.content
    except (ConnectionError, TimeoutError) as e:
        return f"Review connection error: {str(e)}"
    except (ValueError, KeyError) as e:
        return f"Review error: {str(e)}"


def reflection_node(state: AgentState, llm) -> AgentState:
    """Review extracted data for completeness."""
    document_data = state.get("document_data", DocumentData())
    pdf_content = state.get("pdf_content", "")
    retry_count = state.get("retry_count", 0)

    if not pdf_content:
        return {**state, "review_feedback": "No content to review", "is_complete": False}

    # If we've retried too many times, mark as complete to avoid infinite loop
    if retry_count >= 2:
        return {
            **state,
            "review_feedback": "Maximum retries reached. Proceeding with current data.",
            "is_complete": True
        }

    # Use the tool to review data
    feedback = review_extracted_data.invoke({
        "document_data": document_data,
        "pdf_content": pdf_content,
        "llm": llm
    })

    is_complete = "COMPLETE" in feedback.upper() or retry_count >= 2

    return {
        **state,
        "review_feedback": feedback,
        "is_complete": is_complete,
        "retry_count": retry_count + 1
    }
