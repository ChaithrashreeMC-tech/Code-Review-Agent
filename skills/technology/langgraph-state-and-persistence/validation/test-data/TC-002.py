import operator
from typing import Annotated, List, TypedDict

class AuditState(TypedDict):
    task_id: str
    log: Annotated[List[str], operator.add]

