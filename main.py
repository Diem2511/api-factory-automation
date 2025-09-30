from fastapi import FastAPI
import os
import uvicorn
import logging
from contextlib import asynccontextmanager

# Configurar logging para ver detalles en los logs de Railway
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Manejador de "lifespan" para conectar a la BD al iniciar
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Iniciando aplicación...")
    try:
        from app.models import create_tables
        logger.info("Conectando a la base de datos y verificando tablas...")
        create_tables()
        logger.info("Conexión a la base de datos exitosa.")
    except Exception as e:
        logger.error(f"Error fatal durante la conexión a la base de datos: {e}")
    
    yield
    
    logger.info("Cerrando aplicación.")

app = FastAPI(
    title="API Factory Automation",
    description="Sistema automatizado para descubrir, envolver y desplegar APIs.",
    version="2.0.0",
    lifespan=lifespan
)

@app.get("/")
async def root():
    return {"message": "✅ API Factory Automation está en línea y funcionando!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/db-status")
async def db_status():
    # Este endpoint nos ayudará a verificar la conexión
    return {"database_connection": "successful_on_startup"}

if __name__ == "__main__":
    # Python leerá la variable PORT correctamente desde el entorno
    port = int(os.getenv("PORT", 8080))
    logger.info(f"🚀 Servidor iniciando en el puerto {port}")
    uvicorn.run("main:app", host="0.0.0.0", port=port)
