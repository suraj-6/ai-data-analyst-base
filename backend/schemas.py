from pydantic import BaseModel
from typing import Optional

class QuestionRequest(BaseModel):
    """What the frontend sends to the backend."""
    question: str

class AnalysisResponse(BaseModel):
    """What the backend sends back to the frontend."""
    answer:     str
    sql_query:  str
    chart_json: Optional[str] = None
    reasoning:  list[str]