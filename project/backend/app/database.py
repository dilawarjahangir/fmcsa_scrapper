import os
from contextlib import contextmanager

import psycopg2
from psycopg2.extras import RealDictCursor

DB_HOST     = os.getenv("POSTGRES_HOST", "localhost")
DB_NAME     = os.getenv("POSTGRES_DB",   "my_fmcsa_db")
DB_USER     = os.getenv("POSTGRES_USER", "postgres")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "1234")
DB_PORT     = os.getenv("POSTGRES_PORT", "5432")

@contextmanager
def get_db_connection():
    conn = psycopg2.connect(
        host=DB_HOST, port=DB_PORT, dbname=DB_NAME,
        user=DB_USER, password=DB_PASSWORD,
        cursor_factory=RealDictCursor,
    )
    try:
        yield conn
    finally:
        conn.close()

def get_last_mc_scraped(cur) -> int:
    """Return the most‑recent MC number saved by the batch job."""
    cur.execute("SELECT last_mc_scraped FROM scraper_state LIMIT 1")
    row = cur.fetchone()
    return row["last_mc_scraped"] if row else 0

def set_last_mc_scraped(cur, mc: int) -> None:
    """Persist the pointer after each successful batch run."""
    cur.execute(
        "UPDATE scraper_state SET last_mc_scraped = %s, updated_at = now()",
        (mc,),
    )

def init_db():
    # carriers table (with lead flag)
    cur_sql = """
    CREATE TABLE IF NOT EXISTS carriers (
      id SERIAL PRIMARY KEY,
      mc_number        VARCHAR(50) UNIQUE NOT NULL,
      data             JSONB,
      mcs150_form_date DATE,
      called           BOOLEAN NOT NULL DEFAULT FALSE,
      lead             BOOLEAN NOT NULL DEFAULT FALSE,
      created_at       TIMESTAMP WITH TIME ZONE DEFAULT now(),
      updated_at       TIMESTAMP WITH TIME ZONE DEFAULT now()
    );
    """
    # leads table (same schema, minus trigger)
    leads_sql = """
    CREATE TABLE IF NOT EXISTS leads (
      id SERIAL PRIMARY KEY,
      mc_number        VARCHAR(50) UNIQUE NOT NULL,
      data             JSONB,
      mcs150_form_date DATE,
      called           BOOLEAN NOT NULL DEFAULT FALSE,
      lead             BOOLEAN NOT NULL DEFAULT FALSE,
      created_at       TIMESTAMP WITH TIME ZONE,
      updated_at       TIMESTAMP WITH TIME ZONE
    );
    """
    # timestamp trigger for carriers.updated_at
    trigger_fn = """
    CREATE OR REPLACE FUNCTION trigger_set_timestamp()
    RETURNS TRIGGER AS $$
    BEGIN
      NEW.updated_at = now();
      RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    """
    drop_trig   = "DROP TRIGGER IF EXISTS set_timestamp ON carriers;"
    create_trig = """
    CREATE TRIGGER set_timestamp
      BEFORE UPDATE ON carriers
      FOR EACH ROW
      EXECUTE PROCEDURE trigger_set_timestamp();
    """

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(cur_sql)
            cur.execute(leads_sql)
            cur.execute(trigger_fn)
            cur.execute(drop_trig)
            cur.execute(create_trig)
        conn.commit()
