from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date

class QueryRequest(BaseModel):
    mc_number: str

class QueryResponse(BaseModel):
    data: dict
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    mcs150_form_date: Optional[date] = None

class BatchQueryRequest(BaseModel):
    mc_number: str
    till_number: int

class BatchQueryResponse(BaseModel):
    results: dict
