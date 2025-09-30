from fastapi import FastAPI
from contextlib import asynccontextmanager
from sqlalchemy import text
from loguru import logger
from tenacity import retry, wait_fixed, stop_after_delay

from app.db import engine
from app.models import create_tables

@retry(wait=wait_fixed(2), stop=stop_after_delay(40))
def init_db():
    # verifica conexión
    with engine.begin() as conn:
        conn.execute(text("SELECT 1"))
    # crea tablas (no hace nada si ya existen)
    create_tables(engine)
    logger.info("DB ready.")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing DB...")
    init_db()
    yield

app = FastAPI(title="API Factory Automation", lifespan=lifespan)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/")
def root():
    return {"ok": True}
