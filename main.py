from fastapi import FastAPI
import os
import uvicorn
import logging

# Configurar logging para ver más detalles
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="API Factory - Safe Mode",
    version="0.0.1"
)

@app.get("/")
async def root():
    logger.info("Root endpoint was hit!")
    return {"message": "API is running in Safe Mode."}

@app.get("/health")
async def health_check():
    logger.info("Health check was successful!")
    return {"status": "healthy_in_safe_mode"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    logger.info(f"🚀 Starting SAFE MODE server on http://0.0.0.0:{port}")
    uvicorn.run("main:app", host="0.0.0.0", port=port)
