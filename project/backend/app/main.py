from fastapi import FastAPI
from app.routes import query
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
    title="FMCSA Query API",
    description="API to query FMCSA data using FastAPI and BeautifulSoup.",
)



app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=".*",  # Allow all origins using a regex
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include our query router with a prefix (e.g. /api)
app.include_router(query.router, prefix="/api")
