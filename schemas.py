from pydantic import BaseModel
from typing import Literal

class Decision(BaseModel):
    decision: str
    status: Literal["final", "provisional", "unresolved"]
    condition: str | None = None
    owner: str | None = None
    source_quote: str

class ActionItem(BaseModel):
    task: str 
    owner: str | None = None
    due_date: str | None= None
    source_quote: str 

class Extraction(BaseModel):
    decisions: list[Decision]
    action_items: list[ActionItem]
