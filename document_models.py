from typing import List, TypedDict

from pydantic import BaseModel

# Party model for document parties with roles
class Party(BaseModel):
    name: str = ""
    role: str = ""

# Creating a Pydantic model for document data
class DocumentData(BaseModel):
    document_senderparty: List[Party] = []
    document_recipientparty: List[Party] = []
    document_type: str = ""
    document_date: str = ""
    document_description: str = ""  # Full narrative summary of the document
    document_mainreference: str = ""
    document_otherreferences: List[str] = []  # List of other references mentioned in the document

# Creating a class for the agent state
class AgentState(TypedDict):
    file_path: str
    pdf_content: str
    document_data: DocumentData
    review_feedback: str
    formatted_output: str
    is_complete: bool
    retry_count: int
