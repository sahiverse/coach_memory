# main.py
from fastapi import FastAPI
from contextlib import asynccontextmanager
from database.sql_db import create_all_tables
from api.routes import router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create all SQL tables if they don't exist
    create_all_tables()
    print("✅ Database tables ready.")
    yield
    # Shutdown: nothing to clean up for now

app = FastAPI(
    title="Vani.coach API",
    description="AI-powered speech coaching with 3-layer memory architecture",
    version="0.1.0",
    lifespan=lifespan
)

app.include_router(router, prefix="/api/v1")

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Vani.coach API is running"}
