from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
import os
import uvicorn

from app.models import create_tables, get_db, APIEndpoint

app = FastAPI(
    title="API Factory Automation",
    description="Sistema automatizado para descubrir, envolver y desplegar APIs", 
    version="1.0.0"
)

# Crear tablas al iniciar
@app.on_event("startup")
async def startup_event():
    create_tables()
    print("✅ Tablas de base de datos creadas/verificadas")

# Endpoints básicos
@app.get("/")
async def root():
    return {"message": "API Factory Automation System - Deployed on Railway!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "environment": "production"}

@app.get("/endpoints")
async def list_endpoints(db: Session = Depends(get_db)):
    endpoints = db.query(APIEndpoint).filter(APIEndpoint.is_active == True).all()
    return {"endpoints": endpoints}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
