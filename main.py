from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os
import uvicorn
from app.models import create_tables, get_db, APIEndpoint, APIService
from app.routes import discovery, wrappers, deployment, dashboard

app = FastAPI(
    title="API Factory Automation",
    description="Sistema automatizado para descubrir, envolver y desplegar APIs", 
    version="1.0.0"
)

# Montar archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# Incluir routers
app.include_router(discovery.router)
app.include_router(wrappers.router)
app.include_router(deployment.router)
app.include_router(dashboard.router)

@app.on_event("startup")
async def startup_event():
    try:
        create_tables()
        print("🚀 API Factory Automation iniciada correctamente")
    except Exception as e:
        print(f"⚠️ Error al crear tablas: {e}")

# Servir el HTML directamente en la raíz
@app.get("/", response_class=FileResponse)
async def root():
    return FileResponse('static/index.html')

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "api-factory-automation"}

@app.get("/api/endpoints")
async def list_endpoints(db: Session = Depends(get_db)):
    endpoints = db.query(APIEndpoint).filter(APIEndpoint.is_active == True).all()
    return {"endpoints": [{"id": e.id, "name": e.name, "url": e.url, "method": e.method} for e in endpoints]}

@app.post("/api/endpoints")
async def create_endpoint(name: str, url: str, method: str = "GET", description: str = "", db: Session = Depends(get_db)):
    endpoint = APIEndpoint(name=name, url=url, method=method, description=description)
    db.add(endpoint)
    db.commit()
    db.refresh(endpoint)
    return {"message": "Endpoint creado exitosamente", "endpoint": {"id": endpoint.id, "name": endpoint.name}}

@app.get("/api/services")
async def list_services(db: Session = Depends(get_db)):
    services = db.query(APIService).filter(APIService.is_active == True).all()
    return {"services": [{"id": s.id, "name": s.name} for s in services]}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
