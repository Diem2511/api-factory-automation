from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
import os
import uvicorn

from app.models import create_tables, get_db, APIEndpoint, APIService
from app.routes import discovery, wrappers

app = FastAPI(
    title="API Factory Automation",
    description="Sistema automatizado para descubrir, envolver y desplegar APIs", 
    version="1.0.0"
)

# Incluir routers
app.include_router(discovery.router)
app.include_router(wrappers.router)

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

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
