from datetime import datetime

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool

from document_models import AgentState, DocumentData

LEGAL_FORMAT_PROMPT = '''
You are a legal document formatter specializing in creating formal chronological summaries for legal proceedings.

Your task is to format the provided document data into a formal, legal-sound chronological entry that follows this EXACT format:

"On [Date of the document], [Sender Party] sent [Type of document] to the [Recipient Party] [Description of the document in legal writing], via ref. [Main Reference of the Document]."

CRITICAL REQUIREMENTS:
1. **Use ROLES not NAMES**: Always use the party's role (e.g., "Contractor", "Engineer", "Owner", "Consultant") instead of their actual name
2. **Date Format**: Convert the date to "DD Month YYYY" format (e.g., "25 December 2024")
3. **Sender/Recipient Clarity**: Clearly identify the sender party role and recipient party role from the document data
4. **Legal Tone**: Use formal, professional legal language
5. **Precision**: Include all relevant details without summarization
6. **Consistency**: Maintain the exact format structure provided
7. **Completeness**: Ensure all document details are accurately represented

FORMAT BREAKDOWN:
- [Date of the document]: Use formatted date (DD Month YYYY)
- [Sender Party]: Use the role of the sending party
- [Type of document]: Use the document type
- [Recipient Party]: Use the role of the receiving party
- [Description of the document]: Use the full document description in legal writing style
- [Main Reference of the Document]: Use the main reference number/code


IMPORTANT: Create a single, cohesive paragraph that includes the main document information and any related events in chronological order. Do not create separate sections or bullet points.

Use formal legal terminology and ensure the text is suitable for legal documentation and court proceedings.
REMEMBER: Always use the party ROLE, never the actual name in the final output.
'''


def format_date_legal(date_str: str) -> str:
    """Convert YYYY-MM-DD format to DD Month YYYY format."""
    if not date_str:
        return "Date Unknown"

    try:
        # Parse the date string
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        # Format to DD Month YYYY
        return date_obj.strftime("%d %B %Y")
    except ValueError:
        # If parsing fails, return the original string
        return date_str


@tool
def format_document_chronology_llm(document_data: DocumentData, llm) -> str:
    """Format document data into formal legal chronological narrative using LLM."""
    if not document_data.document_date or (not document_data.document_senderparty and not document_data.document_recipientparty):
        return "Insufficient data for formatting"

    # Format the date
    formatted_date = format_date_legal(document_data.document_date)

    # Get sender and recipient party roles
    sender_party_role = document_data.document_senderparty[0].role if document_data.document_senderparty else "Unknown Sender"
    recipient_party_role = document_data.document_recipientparty[0].role if document_data.document_recipientparty else "Unknown Recipient"

    # Prepare party information for LLM
    sender_parties_info = []
    for party in document_data.document_senderparty:
        sender_parties_info.append(f"{party.name} ({party.role})")

    recipient_parties_info = []
    for party in document_data.document_recipientparty:
        recipient_parties_info.append(f"{party.name} ({party.role})")

    # Smart reference formatting - check if document type is already in the reference
    main_reference = document_data.document_mainreference or ""
    document_type = document_data.document_type or ""

    # Check if document type (or part of it) is already in the reference
    if document_type and main_reference:
        document_type_lower = document_type.lower()
        main_reference_lower = main_reference.lower()

        # If document type is not already in the reference, add it
        if document_type_lower not in main_reference_lower:
            formatted_reference = f"{document_type} {main_reference}"
        else:
            formatted_reference = main_reference
    else:
        formatted_reference = main_reference or document_type or "Unknown Reference"

    # Prepare data summary for LLM
    data_summary = f"""
    Document Type: {document_data.document_type}
    Document Date: {formatted_date}
    Document Description: {document_data.document_description}
    Document Sender Parties: {', '.join(sender_parties_info) if sender_parties_info else 'None'}
    Document Recipient Parties: {', '.join(recipient_parties_info) if recipient_parties_info else 'None'}
    Document Main Reference: {document_data.document_mainreference}

    FORMATTING INSTRUCTIONS:
    - Use the required format structure (use ROLE not name):
    "On {formatted_date}, {sender_party_role} sent {document_data.document_type} to the {recipient_party_role} [ENHANCED DESCRIPTION], via ref. {formatted_reference}."
    - Ensure the narrative flows naturally and professionally
    - The reference "{formatted_reference}" has been intelligently formatted to avoid duplication
    """

    messages = [
        SystemMessage(content=LEGAL_FORMAT_PROMPT),
        HumanMessage(content=data_summary)
    ]

    try:
        response = llm.invoke(messages)
        return response.content.strip()
    except Exception as e:
        print(f"❌ LLM invocation error: {e}")
        # Fallback to basic formatting if LLM fails
        enhanced_description = document_data.document_description
        return f"On {formatted_date}, {sender_party_role} sent {document_data.document_type} to the {recipient_party_role} {enhanced_description}, via ref. {formatted_reference}."


def document_formatter_node(state: AgentState, llm=None) -> AgentState:
    """Format the document data into final output using LLM."""
    document_data = state.get("document_data", DocumentData())

    if not document_data.document_type:
        return {**state, "formatted_output": "No data to format"}

    # Use the LLM-powered tool to format data
    if llm:
        formatted_output = format_document_chronology_llm.invoke({
            "document_data": document_data,
            "llm": llm
        })
    else:
        # Fallback to basic formatting
        sender_party_role = document_data.document_senderparty[0].role if document_data.document_senderparty else "Unknown Sender"
        recipient_party_role = document_data.document_recipientparty[0].role if document_data.document_recipientparty else "Unknown Recipient"
        formatted_date = format_date_legal(document_data.document_date)

        # Smart reference formatting for fallback too
        main_reference = document_data.document_mainreference or ""
        document_type = document_data.document_type or ""

        if document_type and main_reference:
            document_type_lower = document_type.lower()
            main_reference_lower = main_reference.lower()

            if document_type_lower not in main_reference_lower:
                formatted_reference = f"{document_type} {main_reference}"
            else:
                formatted_reference = main_reference
        else:
            formatted_reference = main_reference or document_type or "Unknown Reference"

        enhanced_description = document_data.document_description

        formatted_output = f"On {formatted_date}, {sender_party_role} sent {document_data.document_type} to the {recipient_party_role} {enhanced_description}, via ref. {formatted_reference}."

    return {
        **state,
        "formatted_output": formatted_output
    }
