from fastapi import FastAPI
import os
import uvicorn
import logging

# Configurar logging para ver más detalles
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="API Factory Automation",
    description="Sistema automatizado para descubrir, envolver y desplegar APIs.",
    version="1.0.2"
)

@app.on_event("startup")
async def startup_event():
    logger.info("Application startup sequence initiated.")
    try:
        from app.models import create_tables
        logger.info("Attempting to connect to the database and create tables...")
        create_tables()
        logger.info("Database tables checked/created successfully.")
    except Exception as e:
        # ¡IMPORTANTE! Si hay un error de BD, lo imprimimos en lugar de crashear.
        logger.error(f"FATAL: Could not connect to the database. Error: {e}")
        # Esto permite que la app siga corriendo para poder ver el error.

@app.get("/db-status")
async def db_status():
    # Este endpoint ahora nos dirá si la BD falló
    return {"database": "connection_failed", "error": "Check deployment logs for details."}

@app.get("/")
async def root():
    return {"message": "🎉 API Factory Automation is running on Railway!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "port_used": os.getenv("PORT", "8080")}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    logger.info(f"🚀 Starting server on http://0.0.0.0:{port}")
    uvicorn.run("main:app", host="0.0.0.0", port=port)
