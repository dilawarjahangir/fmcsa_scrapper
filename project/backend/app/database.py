import os
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager

DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_NAME = os.getenv("POSTGRES_DB", "my_fmcsa_db")
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "1234")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")

@contextmanager
def get_db_connection():
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        cursor_factory=RealDictCursor
    )
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS carriers (
        id SERIAL PRIMARY KEY,
        mc_number VARCHAR(50) UNIQUE NOT NULL,
        data JSONB,
        mcs150_form_date DATE,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
    );
    """
    
    alter_table_sql = """
    ALTER TABLE carriers
    ADD COLUMN IF NOT EXISTS mcs150_form_date DATE;
    """
    
    trigger_function_sql = """
    CREATE OR REPLACE FUNCTION trigger_set_timestamp()
    RETURNS TRIGGER AS $$
    BEGIN
        NEW.updated_at = now();
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    """
    
    drop_trigger_sql = "DROP TRIGGER IF EXISTS set_timestamp ON carriers;"
    create_trigger_sql = """
    CREATE TRIGGER set_timestamp
    BEFORE UPDATE ON carriers
    FOR EACH ROW
    EXECUTE PROCEDURE trigger_set_timestamp();
    """

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(create_table_sql)
            cur.execute(alter_table_sql)
            cur.execute(trigger_function_sql)
            cur.execute(drop_trigger_sql)
            cur.execute(create_trigger_sql)
        conn.commit()
