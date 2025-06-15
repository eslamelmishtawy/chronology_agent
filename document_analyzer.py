import json

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool

from document_models import AgentState, DocumentData, Party

ANALYZE_PROMPT = '''
You are a specialized legal document analysis assistant with expertise in construction and project management documents. Your task is to extract ALL available information with maximum completeness and accuracy.

STEP-BY-STEP ANALYSIS PROCESS:

STEP 1: PARTY IDENTIFICATION AND ROLE ANALYSIS
Carefully identify each party mentioned in the document and categorize them:
- Read through the document systematically
- Identify who is SENDING/WRITING the document (document_senderparty)
- Identify who is RECEIVING the document (document_recipientparty)
- For each party, determine their detailed role based on:
  * How they are addressed or referenced in the document
  * Their organizational context (company type, department, division)
  * Their specific actions, responsibilities, or authority mentioned
  * Their relationship to the project (owner, contractor, consultant, etc.)
  * Common industry roles with specific functions (Design Engineer, Project Manager, Construction Manager, Architect, Client Representative, etc.)

STEP 2: COMPREHENSIVE DATA EXTRACTION
Extract the following information comprehensively:

1. Document Type: Identify precisely (letter, email, RFI, IR, submittal, transmittal, VO, SWI, drawing, notice, claim, response, approval, rejection, request, report, minutes, schedule, or other)
2. Document Date: Format as YYYY-MM-DD (extract from headers, content, or signatures)
3. Document Description: Provide a COMPLETE, detailed description following the document's natural order and flow - DO NOT summarize, reorder, or truncate
4. Document Parties: Categorize into sender and recipient parties with detailed roles
5. Document Reference: Extract ALL reference numbers, codes, identifiers, project numbers, file numbers, version numbers

CRITICAL REQUIREMENTS:
- Think step by step when identifying parties and their roles
- Extract EVERY piece of information available - leave nothing out
- Be thorough and exhaustive in your analysis
- FOLLOW THE DOCUMENT'S NATURAL ORDER AND SEQUENCE when creating the description
- Include context, background, and implications mentioned in their original position
- Capture all dates, deadlines, and time references as they appear chronologically
- Include all parties mentioned in any context with their specific roles
- Extract all reference numbers and identifiers
- Do not summarize, reorder, or provide abbreviated descriptions - maintain the document's narrative flow

Format as JSON with the following detailed field specifications:

{
  "document_type": "Precise document type classification (letter, email, RFI, IR, submittal, transmittal, VO, SWI, drawing, notice, claim, response, approval, rejection, request, report, minutes, schedule, memo, contract, agreement, specification, or other specific type)",

  "document_date": "Document date in YYYY-MM-DD format. Extract from document headers, date fields, signatures, or content. If multiple dates exist, use the primary document date (creation/issue date)",

  "document_description": "COMPLETE and COMPREHENSIVE narrative summary of the entire document following the EXACT ORDER and flow of the original document. Structure the summary chronologically as it appears in the document, including ALL of the following in their natural sequence: document opening/header context, document purpose and objective stated at the beginning, background information as presented, detailed description of all requests or decisions made in order, specific actions required or taken as they appear, deadlines and timelines mentioned throughout, technical specifications or requirements in sequence, financial implications if any, project phases or milestones as referenced, consequences or impacts discussed, and closing statements or next steps. This should read like a complete chronological narrative that follows the document's structure from beginning to end - DO NOT reorder, summarize, or abbreviate any content",

  "document_senderparty": [
    {
      "name": "Full name of the sending organization, department, or individual (e.g., 'ABC Construction Company', 'Engineering Department', 'John Smith, Project Manager')",
      "role": "Detailed role description including their function and responsibility in this communication (e.g., 'Main Contractor responsible for construction execution', 'Design Engineer providing technical specifications', 'Project Owner requesting information', 'Consultant providing professional advice')"
    }
  ],

  "document_recipientparty": [
    {
      "name": "Full name of the receiving organization, department, or individual (e.g., 'XYZ Development Corp', 'Project Management Office', 'Jane Doe, Architect')",
      "role": "Detailed role description including their function and responsibility as recipient (e.g., 'Project Owner responsible for approvals', 'Consulting Engineer reviewing submissions', 'Contractor receiving instructions', 'Client making decisions')"
    }
  ],

  "document_mainreference": "Main reference number, code, or identifier for the document. This should be the primary reference used to track or identify this document in project records",
  "document_otherreferences": [
    "List of other reference numbers, codes, or identifiers mentioned in the document that do not fit the main reference category. Include all relevant references that provide additional context or information related to the document"
  ]

}

Guidelines for party role identification:
- Consider the organizational context and industry standards
- Look for titles, signatures, and letterheads for clues
- Analyze the nature of communication (who is requesting, approving, responding)
- Use common construction/project management roles when appropriate
- Be specific about roles (e.g., "Design Engineer" vs just "Engineer")
'''


def extract_json_from_response(content: str) -> dict:
    """Extract and parse JSON from LLM response content."""
    # Extract JSON from markdown code blocks if present
    if content.startswith("```json"):
        # Remove markdown code block wrapper
        content = content[7:]  # Remove ```json
        if content.endswith("```"):
            content = content[:-3]  # Remove closing ```
        content = content.strip()
    elif content.startswith("```"):
        # Remove generic markdown code block wrapper
        content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()

    # Try to parse JSON
    return json.loads(content)


def convert_parties_to_objects(analysis_result: dict) -> tuple:
    """Convert party data dictionaries to Party objects for sender and recipient parties."""
    sender_parties = []
    recipient_parties = []

    if "document_senderparty" in analysis_result:
        for party_data in analysis_result["document_senderparty"]:
            sender_parties.append(Party(**party_data))

    if "document_recipientparty" in analysis_result:
        for party_data in analysis_result["document_recipientparty"]:
            recipient_parties.append(Party(**party_data))

    return sender_parties, recipient_parties


def invoke_llm_for_analysis(llm, messages):
    """Wrapper function for LLM invocation for document analysis."""
    return llm.invoke(messages)


@tool
def analyze_document_content(pdf_content: str, llm) -> dict:
    """Analyze PDF content and extract structured data."""
    if not pdf_content:
        return {}

    messages = [
        SystemMessage(content=ANALYZE_PROMPT),
        HumanMessage(content=pdf_content)
    ]

    try:
        print("🤖 Analyzing document with LLM...")
        response = invoke_llm_for_analysis(llm, messages)
        print(response)

        # Extract and parse JSON from response
        content = response.content.strip()
        parsed_result = extract_json_from_response(content)
        print("✅ Extracted document data successfully")
        return parsed_result

    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error: {e}")
        return {}
    except (ConnectionError, TimeoutError) as e:
        print(f"❌ LLM connection error: {e}")
        return {}


def document_analyzer_node(state: AgentState, llm) -> AgentState:
    """Analyze document content and extract structured data."""
    pdf_content = state.get("pdf_content", "")

    if not pdf_content:
        print("❌ No PDF content to analyze")
        return {**state, "is_complete": False}

    # Use the tool to analyze content
    analysis_result = analyze_document_content.invoke({"pdf_content": pdf_content, "llm": llm})

    if analysis_result:
        # Convert parties to Party objects
        sender_parties, recipient_parties = convert_parties_to_objects(analysis_result)
        analysis_result["document_senderparty"] = sender_parties
        analysis_result["document_recipientparty"] = recipient_parties

        # Ensure document_otherreferences is a list if it exists
        if "document_otherreferences" not in analysis_result:
            analysis_result["document_otherreferences"] = []
        elif isinstance(analysis_result["document_otherreferences"], str):
            analysis_result["document_otherreferences"] = [analysis_result["document_otherreferences"]]

        document_data = DocumentData(**analysis_result)
        return {**state, "document_data": document_data}

    print("❌ Analysis failed")
    return {**state, "document_data": DocumentData()}
