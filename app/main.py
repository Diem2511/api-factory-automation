from fastapi import FastAPI
from contextlib import asynccontextmanager
from loguru import logger
from sqlalchemy import text
from tenacity import retry, wait_fixed, stop_after_delay

from .db import Base, engine
from .routers import health, discovery, wrappers

@retry(wait=wait_fixed(2), stop=stop_after_delay(40))
def init_db():
    with engine.begin() as conn:
        conn.execute(text("SELECT 1"))
    Base.metadata.create_all(bind=engine)
    logger.info("DB ready and tables created.")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing DB...")
    init_db()
    yield

app = FastAPI(title="API Factory Automation", lifespan=lifespan)
app.include_router(health.router)
app.include_router(discovery.router)
app.include_router(wrappers.router)
