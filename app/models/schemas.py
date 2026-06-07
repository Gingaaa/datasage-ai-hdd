from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict

class ColumnDefinition(BaseModel):
    name: str
    type: str
    description: str
    inferred_relationship: Optional[str] = None

class DataDictionary(BaseModel):
    dataset_description: str
    columns: List[ColumnDefinition]

class ChatRequest(BaseModel):
    message: str = Field(..., description="The query to ask the agent")

class ChatResponse(BaseModel):
    reply: str
    chart_data: Optional[Dict[str, Any]] = None
