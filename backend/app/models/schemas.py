from pydantic import BaseModel
from typing import List

class QueryRequest(BaseModel):
    documents: str          # PDF blob URL
    questions: List[str]    # List of NL questions

class QueryResponse(BaseModel):
    answers: List[str]      # Same order as questions — CRITICAL!