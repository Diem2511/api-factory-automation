from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
import os
import uvicorn

# Importar después de asegurar dependencias
try:
    from app.models import create_tables, get_db, APIEndpoint
    from app.config import settings
except ImportError as e:
    print(f"Import error: {e}")

app = FastAPI(
    title="API Factory Automation",
    description="Sistema automatizado para descubrir, envolver y desplegar APIs", 
    version="1.0.0"
)

# Endpoints básicos - SIN base de datos por ahora
@app.get("/")
async def root():
    return {"message": "API Factory Automation System - Deployed on Railway!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "environment": "production"}

# Endpoint simple sin base de datos
@app.get("/test")
async def test():
    return {"test": "ok", "port": os.getenv("PORT", "8000")}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    print(f"🚀 Starting server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
