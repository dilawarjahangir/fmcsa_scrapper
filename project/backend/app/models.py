from pydantic import BaseModel

class QueryRequest(BaseModel):
    mc_number: str

class QueryResponse(BaseModel):
    data: dict

# New models for batch query
class BatchQueryRequest(BaseModel):
    mc_number: str
    till_number: int

class BatchQueryResponse(BaseModel):
    results: dict
