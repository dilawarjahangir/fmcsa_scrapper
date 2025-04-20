# app/routes/query.py

from datetime import datetime
import json
from typing import Dict, Any, List, Optional

from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel
from psycopg2.errors import UniqueViolation

from app.database import get_db_connection
from app.models import (
    QueryRequest,
    QueryResponse,
    BatchQueryRequest,
    BatchQueryResponse,
)
from app.scraper import get_carrier_info

router = APIRouter()


def parse_mcs150_date(date_str: str) -> Optional[datetime.date]:
    try:
        return datetime.strptime(date_str, "%m/%d/%Y").date()
    except:
        return None


def is_data_meaningful(data: Dict[str, Any]) -> bool:
    return any(v.strip() for section in data.values() for v in section.values())


@router.post("/carrier", response_model=QueryResponse)
async def query_carrier(info: QueryRequest):
    mc = info.mc_number
    with get_db_connection() as conn, conn.cursor() as cur:
        cur.execute("""
            SELECT mc_number, data, created_at, updated_at,
                   mcs150_form_date, called, lead
              FROM carriers WHERE mc_number = %s
        """, (mc,))
        if (row := cur.fetchone()):
            return QueryResponse(**row)

        try:
            data, raw = get_carrier_info(mc)
        except Exception as exc:
            raise HTTPException(502, str(exc))

        if not is_data_meaningful(data):
            raise HTTPException(404, f"No FMCSA data for MC {mc}")

        mcs150_date = parse_mcs150_date(raw) if raw else None
        try:
            cur.execute("""
                INSERT INTO carriers
                  (mc_number, data, mcs150_form_date)
                VALUES (%s, %s, %s)
                RETURNING mc_number, data, created_at, updated_at,
                          mcs150_form_date, called, lead
            """, (mc, json.dumps(data, ensure_ascii=False), mcs150_date))
            record = cur.fetchone()
            conn.commit()
        except UniqueViolation:
            conn.rollback()
            raise HTTPException(409, "MC number already exists.")

    return QueryResponse(**record)


@router.post("/carrier/batch", response_model=BatchQueryResponse)
async def query_carrier_batch(info: BatchQueryRequest):
    """
    Attempts info.till_number carriers starting at info.mc_number.
    On scrape errors records {"error": "..."} and continues.
    """
    try:
        start_mc = int(info.mc_number)
    except ValueError:
        raise HTTPException(400, "mc_number must be numeric")

    results: Dict[str, Any] = {}
    with get_db_connection() as conn, conn.cursor() as cur:
        for offset in range(info.till_number):
            mc = str(start_mc + offset)

            # A) cached?
            cur.execute("""
                SELECT mc_number, data, created_at, updated_at,
                       mcs150_form_date, called, lead
                  FROM carriers WHERE mc_number = %s
            """, (mc,))
            if (row := cur.fetchone()):
                results[mc] = dict(row)
                continue

            # B) scrape
            try:
                data, raw = get_carrier_info(mc)
            except Exception as exc:
                # record the scrape error and move on
                results[mc] = {"error": str(exc)}
                continue

            # C) skip empty placeholder pages
            if not is_data_meaningful(data):
                continue

            mcs150_date = parse_mcs150_date(raw) if raw else None

            # D) insert
            try:
                cur.execute("""
                    INSERT INTO carriers
                      (mc_number, data, mcs150_form_date)
                    VALUES (%s, %s, %s)
                    RETURNING mc_number, data, created_at, updated_at,
                              mcs150_form_date, called, lead
                """, (mc, json.dumps(data, ensure_ascii=False), mcs150_date))
                results[mc] = dict(cur.fetchone())
            except UniqueViolation:
                conn.rollback()
                results[mc] = {"error": "duplicate"}
                continue

        conn.commit()

    return BatchQueryResponse(results=results)


@router.get("/carriers/dates", response_model=List[str])
async def get_run_dates():
    with get_db_connection() as conn, conn.cursor() as cur:
        cur.execute("SELECT DISTINCT DATE(created_at) AS d FROM carriers ORDER BY d DESC")
        return [r["d"].isoformat() for r in cur.fetchall()]


@router.get("/carriers/by-date", response_model=List[QueryResponse])
async def get_by_date(date: str = Query(..., description="YYYY-MM-DD")):
    with get_db_connection() as conn, conn.cursor() as cur:
        cur.execute("""
            SELECT mc_number, data, created_at, updated_at,
                   mcs150_form_date, called, lead
              FROM carriers
             WHERE DATE(created_at) = %s
             ORDER BY mcs150_form_date ASC NULLS LAST, mc_number ASC
        """, (date,))
        rows = cur.fetchall()
    return [QueryResponse(**r) for r in rows]


class CalledUpdate(BaseModel):
    called: bool


@router.patch("/carriers/{mc_number}/called", response_model=QueryResponse)
async def toggle_called(mc_number: str, payload: CalledUpdate = Body(...)):
    with get_db_connection() as conn, conn.cursor() as cur:
        cur.execute("""
            UPDATE carriers
               SET called = %s, updated_at = now()
             WHERE mc_number = %s
         RETURNING mc_number, data, created_at, updated_at,
                   mcs150_form_date, called, lead
        """, (payload.called, mc_number))
        if not (row := cur.fetchone()):
            raise HTTPException(404, f"MC {mc_number} not found")
        conn.commit()
    return QueryResponse(**row)


class LeadToggle(BaseModel):
    lead: bool


@router.patch("/carriers/{mc_number}/lead", response_model=QueryResponse)
async def toggle_lead(mc_number: str, payload: LeadToggle = Body(...)):
    with get_db_connection() as conn, conn.cursor() as cur:
        # Update the flag
        cur.execute("""
            UPDATE carriers
               SET lead = %s, updated_at = now()
             WHERE mc_number = %s
         RETURNING mc_number, data, created_at, updated_at,
                   mcs150_form_date, called, lead
        """, (payload.lead, mc_number))
        row = cur.fetchone()
        if not row:
            raise HTTPException(404, f"MC {mc_number} not found")

        # Serialize JSON and upsert into leads table
        data_json = json.dumps(row["data"], ensure_ascii=False)
        if payload.lead:
            cur.execute("""
                INSERT INTO leads (
                  mc_number, data, created_at, updated_at,
                  mcs150_form_date, called, lead
                )
                VALUES (
                  %s, %s::jsonb, %s, %s, %s, %s, %s
                )
                ON CONFLICT (mc_number) DO UPDATE
                  SET lead = EXCLUDED.lead,
                      data = EXCLUDED.data,
                      updated_at = EXCLUDED.updated_at
            """, (
                row["mc_number"],
                data_json,
                row["created_at"],
                row["updated_at"],
                row["mcs150_form_date"],
                row["called"],
                row["lead"],
            ))
        else:
            cur.execute("DELETE FROM leads WHERE mc_number = %s", (mc_number,))

        conn.commit()

    return QueryResponse(**row)
