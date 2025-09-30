from fastapi import FastAPI
import os
import uvicorn

app = FastAPI(
    title="API Factory Automation",
    description="Sistema automatizado para descubrir, envolver y desplegar APIs", 
    version="1.0.0"
)

# Intentar importar modelos (pero no fallar si no existen)
try:
    from app.models import create_tables
    
    @app.on_event("startup")
    async def startup_event():
        create_tables()
        print("✅ Tablas de base de datos creadas/verificadas")
        
    @app.get("/db-status")
    async def db_status():
        return {"database": "connected", "status": "ready"}
        
except ImportError as e:
    print(f"⚠️  Dependencias de base de datos no disponibles: {e}")
    
    @app.get("/db-status")
    async def db_status():
        return {"database": "not_available", "message": "Dependencias faltan"}

@app.get("/")
async def root():
    return {"message": "🎉 ¡API Factory Automation funcionando en Railway!"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "environment": "production",
        "port": os.getenv("PORT", "8080")
    }

@app.get("/test")
async def test_endpoint():
    return {"test": "success", "message": "¡Todo funciona correctamente!"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))  # Usar 8080 que es el de Railway
    print(f"🚀 Iniciando servidor en puerto {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
