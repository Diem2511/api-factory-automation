from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.services.wrapper_service import APIWrapperService
from app.models import get_db, APIEndpoint, WrapperConfig
import json

router = APIRouter(prefix="/wrappers", tags=["wrappers"])

@router.post("/generate")
async def generate_wrapper(
    base_url: str,
    wrapper_type: str = "rest",
    db: Session = Depends(get_db)
):
    """Genera un wrapper automático para una API"""
    try:
        # Obtener endpoints existentes para esta base URL
        endpoints = db.query(APIEndpoint).filter(
            APIEndpoint.url.like(f"%{base_url}%"),
            APIEndpoint.is_active == True
        ).all()
        
        if not endpoints:
            raise HTTPException(
                status_code=404, 
                detail=f"No se encontraron endpoints para {base_url}. Ejecuta /discovery/discover primero."
            )
        
        wrapper_service = APIWrapperService()
        
        # Convertir endpoints a formato para el wrapper
        endpoint_data = [
            {
                "url": endpoint.url.replace(base_url, ""),
                "method": endpoint.method,
                "description": endpoint.description or ""
            }
            for endpoint in endpoints
        ]
        
        if wrapper_type == "rest":
            result = wrapper_service.create_rest_wrapper(base_url, endpoint_data)
        elif wrapper_type == "graphql":
            result = wrapper_service.create_graphql_wrapper(base_url)
        else:
            raise HTTPException(status_code=400, detail="Tipo de wrapper no soportado")
        
        # Guardar configuración del wrapper
        wrapper_config = WrapperConfig(
            name=f"wrapper_{base_url.replace('https://', '').replace('/', '_')}",
            target_api_id=None,  # Podría vincularse a un APIService específico
            wrapper_type=wrapper_type,
            config=result["config"]
        )
        
        db.add(wrapper_config)
        db.commit()
        
        return {
            "message": f"Wrapper {wrapper_type} generado exitosamente",
            "wrapper_config_id": wrapper_config.id,
            "endpoints_wrapped": len(endpoints),
            "wrapper_code_preview": result["wrapper_code"][:500] + "..." if len(result["wrapper_code"]) > 500 else result["wrapper_code"],
            "download_url": f"/wrappers/{wrapper_config.id}/download"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando wrapper: {str(e)}")

@router.get("/{wrapper_id}/download")
async def download_wrapper(wrapper_id: int, db: Session = Depends(get_db)):
    """Descarga el código completo del wrapper"""
    wrapper_config = db.query(WrapperConfig).filter(WrapperConfig.id == wrapper_id).first()
    if not wrapper_config:
        raise HTTPException(status_code=404, detail="Wrapper no encontrado")
    
    # Re-generar el wrapper (en una implementación real, se guardaría el código)
    wrapper_service = APIWrapperService()
    
    if wrapper_config.wrapper_type == "rest":
        # Obtener endpoints para regenerar el wrapper
        endpoints = db.query(APIEndpoint).filter(APIEndpoint.is_active == True).all()
        endpoint_data = [
            {
                "url": endpoint.url,
                "method": endpoint.method,
                "description": endpoint.description or ""
            }
            for endpoint in endpoints
        ]
        
        base_url = wrapper_config.config.get("base_url", "https://api.example.com")
        result = wrapper_service.create_rest_wrapper(base_url, endpoint_data)
        code = result["wrapper_code"]
    
    else:
        endpoint_url = wrapper_config.config.get("endpoint_url", "https://api.example.com/graphql")
        result = wrapper_service.create_graphql_wrapper(endpoint_url)
        code = result["wrapper_code"]
    
    return {
        "filename": f"api_wrapper_{wrapper_id}.py",
        "content": code,
        "wrapper_type": wrapper_config.wrapper_type
    }

@router.get("/")
async def list_wrappers(db: Session = Depends(get_db)):
    """Lista todos los wrappers generados"""
    wrappers = db.query(WrapperConfig).filter(WrapperConfig.is_active == True).all()
    
    return {
        "wrappers": [
            {
                "id": wrapper.id,
                "name": wrapper.name,
                "wrapper_type": wrapper.wrapper_type,
                "created_at": wrapper.created_at.isoformat() if wrapper.created_at else None,
                "endpoints_count": len(wrapper.config.get("endpoints", [])) if wrapper.config else 0
            }
            for wrapper in wrappers
        ]
    }

@router.post("/test/{wrapper_id}")
async def test_wrapper(wrapper_id: int, method: str, endpoint: str, db: Session = Depends(get_db)):
    """Prueba un wrapper específico"""
    # En una implementación completa, aquí se ejecutaría el código del wrapper
    # Por ahora, simulamos una respuesta
    
    return {
        "message": "Wrapper test ejecutado",
        "wrapper_id": wrapper_id,
        "method": method,
        "endpoint": endpoint,
        "result": "simulated_response",
        "status": "success"
    }
