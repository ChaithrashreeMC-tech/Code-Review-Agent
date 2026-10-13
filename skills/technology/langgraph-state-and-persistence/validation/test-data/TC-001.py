from typing import TypedDict, List
from typing_extensions import NotRequired

class DocumentWorkflowState(TypedDict):
    doc_id: str
    query: str
    summary: NotRequired[str]
    citations: NotRequired[List[str]]

