from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from .database import get_db
from .models.api_opportunity import ApiOpportunity
import os

app = FastAPI(title="API Factory Automation", version="1.0.0")

@app.get("/")
async def root():
    return {"message": "API Factory Automation System Running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "api-factory"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
