from fastapi import FastAPI
import os
import uvicorn

app = FastAPI(
    title="API Factory Automation",
    description="Sistema automatizado para descubrir, envolver y desplegar APIs.",
    version="1.0.1"
)

try:
    from app.models import create_tables

    @app.on_event("startup")
    async def startup_event():
        print("✅ Application startup: creating database tables.")
        create_tables()

    @app.get("/db-status")
    async def db_status():
        return {"database": "connected", "status": "tables_initialized"}

except ImportError as e:
    print(f"⚠️  Database models could not be imported: {e}")

    @app.get("/db-status")
    async def db_status_failed():
        return {"database": "not_available", "reason": str(e)}

@app.get("/")
async def root():
    return {"message": "🎉 API Factory Automation is running on Railway!"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "port_used": os.getenv("PORT", "8080")
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    print(f"🚀 Starting server on http://0.0.0.0:{port}")
    # Se quita reload=True para producción
    uvicorn.run("main:app", host="0.0.0.0", port=port)
