"""TC-001: Correct tool schemas and model-tool binding."""
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from typing import Optional

class SearchQuery(BaseModel):
    query: str = Field(description="Search terms for finding documentation")
    limit: Optional[int] = Field(default=5, description="Maximum number of results to return")

@tool(args_schema=SearchQuery)
def search_documentation(query: str, limit: Optional[int] = 5) -> list[str]:
    """Search the developer documentation library for matching articles."""
    return [f"Doc result for: {query}"]

def bind_tools_to_model(llm):
    return llm.bind_tools([search_documentation])

