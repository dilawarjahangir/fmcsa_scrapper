from fastapi import APIRouter, HTTPException
from app.models import QueryRequest, QueryResponse, BatchQueryRequest, BatchQueryResponse
from app.scraper import get_carrier_info

router = APIRouter()

@router.post("/carrier", response_model=QueryResponse)
async def query_carrier(info: QueryRequest):
    """
    Endpoint to query FMCSA data for a given MC number.
    """
    try:
        data = get_carrier_info(info.mc_number)
        return QueryResponse(data=data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/carrier/batch", response_model=BatchQueryResponse)
async def query_carrier_batch(info: BatchQueryRequest):
    """
    Endpoint to query FMCSA data for a range of MC numbers.
    Starting from the provided mc_number, it increments the MC number by 1
    until reaching the count specified by till_number.
    """
    results = {}
    try:
        # Convert the starting MC number to integer for incrementing.
        start_mc = int(info.mc_number)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid mc_number provided, must be numeric.")
    
    # Loop for the count of till_number and gather data for each MC.
    for i in range(info.till_number):
        current_mc = str(start_mc + i)
        try:
            carrier_data = get_carrier_info(current_mc)
            results[current_mc] = carrier_data
        except Exception as e:
            results[current_mc] = {"error": str(e)}
    
    return BatchQueryResponse(results=results)
