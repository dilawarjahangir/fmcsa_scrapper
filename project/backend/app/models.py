from typing import Optional, Dict, Any
from datetime import datetime, date
from pydantic import BaseModel

class QueryRequest(BaseModel):
    mc_number: str

class QueryResponse(BaseModel):
    mc_number: str
    data: Dict[str, Any]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    mcs150_form_date: Optional[date] = None
    called: bool
    lead:   bool

class BatchQueryRequest(BaseModel):
    mc_number: str
    till_number: int

class BatchQueryResponse(BaseModel):
    results: dict
