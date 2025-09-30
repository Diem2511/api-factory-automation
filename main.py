from fastapi import FastAPI
import os

app = FastAPI(
    title="API Factory Automation",
    description="Sistema automatizado para descubrir, envolver y desplegar APIs", 
    version="1.0.0"
)

@app.get("/")
async def root():
    return {"message": "🎉 ¡API Factory Automation funcionando en Railway!"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "environment": "production",
        "port": os.getenv("PORT", "8000")
    }

@app.get("/test")
async def test_endpoint():
    return {"test": "success", "message": "Todo funciona correctamente"}

# Solo intentar importar la base de datos si las dependencias están disponibles
try:
    from app.models import create_tables
    
    @app.on_event("startup")
    async def startup_event():
        create_tables()
        print("✅ Tablas de base de datos creadas/verificadas")
        
    @app.get("/db-test")
    async def db_test():
        return {"database": "connected", "tables": "created"}
        
except ImportError as e:
    print(f"⚠️  Algunas dependencias no disponibles: {e}")
    
    @app.get("/db-test")
    async def db_test():
        return {"database": "not_available", "message": "Algunas dependencias faltan"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    print(f"🚀 Iniciando servidor en puerto {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
