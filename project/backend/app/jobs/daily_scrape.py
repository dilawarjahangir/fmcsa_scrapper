# app/jobs/daily_scrape.py

"""
Runs once a day and pulls the next 500 MC numbers into the DB.
The pointer is saved in scraper_state.last_mc_scraped.
"""
import json
from datetime import datetime

from app.database import (
    get_db_connection,
    get_last_mc_scraped,
    set_last_mc_scraped,
)
from app.scraper import get_carrier_info
from app.routes.query import is_data_meaningful, parse_mcs150_date

# how many *successful* inserts to do per run
BATCH_SAVE_LIMIT = 500
def run_daily_batch() -> None:
    with get_db_connection() as conn, conn.cursor() as cur:
        # start just after the last one we scraped
        next_mc = get_last_mc_scraped(cur) + 1
        saved = 0

        # keep trying MC numbers until we've saved 500 new carriers
        while saved < BATCH_SAVE_LIMIT:
            mc = str(next_mc)

            # skip if already in DB
            cur.execute("SELECT 1 FROM carriers WHERE mc_number = %s", (mc,))
            if cur.fetchone():
                next_mc += 1
                continue

            # scrape it
            try:
                data, mcs150_raw = get_carrier_info(mc)
            except Exception as exc:
                print(f"[{datetime.now()}] MC {mc}: scrape error → {exc}")
                next_mc += 1
                continue

            # skip “no match” pages
            if not is_data_meaningful(data):
                next_mc += 1
                continue

            # parse date if present
            mcs150_date = parse_mcs150_date(mcs150_raw) if mcs150_raw else None

            # insert into carriers
            cur.execute(
                """
                INSERT INTO carriers (mc_number, data, mcs150_form_date)
                VALUES (%s, %s, %s)
                """,
                (mc, json.dumps(data, ensure_ascii=False), mcs150_date),
            )
            saved += 1
            next_mc += 1

        # persist pointer to the last attempted MC number
        set_last_mc_scraped(cur, next_mc - 1)
        conn.commit()
        print(f"[{datetime.now()}] Batch done → saved {saved} records, up to MC {next_mc - 1}")
