from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import os
import uvicorn

from app.models import create_tables, get_db, APIEndpoint, APIService

app = FastAPI(
    title="API Factory Automation",
    description="Sistema automatizado para descubrir, envolver y desplegar APIs", 
    version="1.0.0"
)

# Evento de startup - crear tablas
@app.on_event("startup")
async def startup_event():
    try:
        create_tables()
        print("🚀 API Factory Automation iniciada correctamente")
    except Exception as e:
        print(f"⚠️ Error al crear tablas: {e}")

# Endpoints básicos
@app.get("/")
async def root():
    return {"message": "✅ API Factory Automation está en línea y funcionando!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "api-factory-automation"}

# Endpoints de gestión de APIs
@app.get("/endpoints")
async def list_endpoints(db: Session = Depends(get_db)):
    endpoints = db.query(APIEndpoint).filter(APIEndpoint.is_active == True).all()
    return {"endpoints": endpoints}

@app.post("/endpoints")
async def create_endpoint(
    name: str, 
    url: str, 
    method: str = "GET",
    description: str = "",
    db: Session = Depends(get_db)
):
    endpoint = APIEndpoint(
        name=name,
        url=url, 
        method=method,
        description=description
    )
    db.add(endpoint)
    db.commit()
    db.refresh(endpoint)
    return {"message": "Endpoint creado exitosamente", "endpoint": endpoint}

@app.get("/services")
async def list_services(db: Session = Depends(get_db)):
    services = db.query(APIService).filter(APIService.is_active == True).all()
    return {"services": services}

# Endpoint de prueba de base de datos
@app.get("/db-test")
async def db_test(db: Session = Depends(get_db)):
    try:
        # Crear un endpoint de prueba
        test_endpoint = APIEndpoint(
            name="test_endpoint",
            url="/api/test",
            method="GET",
            description="Endpoint de prueba"
        )
        db.add(test_endpoint)
        db.commit()
        
        # Contar endpoints
        count = db.query(APIEndpoint).count()
        
        return {
            "database": "connected", 
            "endpoints_count": count,
            "test_endpoint_created": True
        }
    except Exception as e:
        return {"database": "error", "error": str(e)}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
