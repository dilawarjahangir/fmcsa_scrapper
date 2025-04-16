from fastapi import APIRouter, HTTPException
from psycopg2.errors import UniqueViolation
import json
from datetime import datetime

from app.models import QueryRequest, QueryResponse, BatchQueryRequest, BatchQueryResponse
from app.scraper import get_carrier_info
from app.database import get_db_connection

router = APIRouter()

def parse_mcs150_date(date_str: str):
    """
    Convert a date string (expected format "MM/DD/YYYY") to a date object.
    Returns None if parsing fails.
    """
    try:
        return datetime.strptime(date_str, "%m/%d/%Y").date()
    except Exception:
        return None

@router.post("/carrier", response_model=QueryResponse)
async def query_carrier(info: QueryRequest):
    """
    Endpoint to query FMCSA data for a given MC number.
    - If the record exists, return it.
    - Otherwise, scrape the data, extract the MCS-150 Form Date separately,
      parse it, and insert a new record with the date saved in mcs150_form_date.
    """
    mc_number = info.mc_number

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Check for an existing record.
            cur.execute(
                "SELECT mc_number, data, created_at, updated_at, mcs150_form_date FROM carriers WHERE mc_number = %s",
                (mc_number,)
            )
            existing = cur.fetchone()

            if existing:
                return QueryResponse(
                    data=existing["data"],
                    created_at=existing["created_at"],
                    updated_at=existing["updated_at"],
                    mcs150_form_date=existing["mcs150_form_date"]
                )

            # Scrape data if no record exists.
            try:
                # Now the scraper returns both full data and the raw MCS-150 date string.
                data, mcs150_date_str = get_carrier_info(mc_number)
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

            mcs150_date = parse_mcs150_date(mcs150_date_str) if mcs150_date_str else None

            # Insert a new record with the parsed MCS-150 Form Date stored separately.
            insert_sql = """
                INSERT INTO carriers (mc_number, data, mcs150_form_date)
                VALUES (%s, %s, %s)
                RETURNING mc_number, data, created_at, updated_at, mcs150_form_date;
            """
            try:
                cur.execute(insert_sql, (mc_number, json.dumps(data), mcs150_date))
            except UniqueViolation:
                conn.rollback()
                raise HTTPException(status_code=409, detail="MC number already exists.")
            record_data = cur.fetchone()
        conn.commit()

    return QueryResponse(
        data=record_data["data"],
        created_at=record_data["created_at"],
        updated_at=record_data["updated_at"],
        mcs150_form_date=record_data["mcs150_form_date"]
    )

@router.post("/carrier/batch", response_model=BatchQueryResponse)
async def query_carrier_batch(info: BatchQueryRequest):
    """
    Endpoint to process a batch of MC numbers.
    For each MC:
      - If the record exists, it is skipped.
      - Otherwise, data is scraped, the MCS-150 Form Date is extracted separately,
        parsed, and the new record is inserted.
    """
    results = {}
    try:
        start_mc = int(info.mc_number)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid mc_number provided; must be numeric.")

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            for i in range(info.till_number):
                current_mc = str(start_mc + i)
                try:
                    cur.execute(
                        "SELECT mc_number, data, created_at, updated_at, mcs150_form_date FROM carriers WHERE mc_number = %s",
                        (current_mc,)
                    )
                    existing = cur.fetchone()

                    if existing:
                        results[current_mc] = dict(existing)
                        continue

                    carrier_data, mcs150_date_str = get_carrier_info(current_mc)
                    mcs150_date = parse_mcs150_date(mcs150_date_str) if mcs150_date_str else None

                    insert_sql = """
                        INSERT INTO carriers (mc_number, data, mcs150_form_date)
                        VALUES (%s, %s, %s)
                        RETURNING mc_number, data, created_at, updated_at, mcs150_form_date;
                    """
                    cur.execute(insert_sql, (current_mc, json.dumps(carrier_data), mcs150_date))
                    inserted_data = cur.fetchone()
                    results[current_mc] = dict(inserted_data)

                except Exception as e:
                    results[current_mc] = {"error": str(e)}

            conn.commit()

    return BatchQueryResponse(results=results)

@router.get("/carriers/sorted", response_model=list[QueryResponse])
async def get_sorted_carriers():
    """
    Retrieve all carriers sorted by their MCS-150 Form Date.
    Records are ordered in ascending order so that the latest form date appears at the end.
    As a secondary sort, records with identical dates will be ordered by their created_at timestamp.
    Records with a NULL mcs150_form_date will be placed last.
    """
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            query = """
                SELECT mc_number, data, created_at, updated_at, mcs150_form_date
                FROM carriers
                ORDER BY mcs150_form_date ASC NULLS LAST;
            """
            cur.execute(query)
            rows = cur.fetchall()
    
    response_list = []
    for row in rows:
        response_list.append(QueryResponse(
            data=row["data"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            mcs150_form_date=row["mcs150_form_date"]
        ))
    return response_list
