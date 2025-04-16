from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app.routes import query

def create_app() -> FastAPI:
    # Initialize the database schema (creates table if not exists)
    init_db()

    app = FastAPI(
        title="FMCSA Query API (Postgres + Timestamps)",
        description="API to query FMCSA data using FastAPI, psycopg2, and Postgres, with date tracking.",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origin_regex=".*",  # Allow all origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(query.router, prefix="/api")
    return app

app = create_app()
