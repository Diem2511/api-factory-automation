from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.services.discovery_service import APIDiscoveryService
from app.models import get_db, APIEndpoint

router = APIRouter(prefix="/discovery", tags=["discovery"])

@router.post("/discover")
async def discover_apis(url: str, db: Session = Depends(get_db)):
    """Descubre automáticamente endpoints API desde una URL"""
    try:
        discovery_service = APIDiscoveryService()
        discovered_endpoints = discovery_service.discover_from_webpage(url)
        
        # Guardar endpoints descubiertos en la base de datos
        saved_count = 0
        for endpoint_data in discovered_endpoints:
            try:
                endpoint = APIEndpoint(
                    name=f"discovered_{endpoint_data['method']}_{saved_count}",
                    url=endpoint_data['url'],
                    method=endpoint_data['method'],
                    description=f"Descubierto automáticamente desde {url}"
                )
                db.add(endpoint)
                saved_count += 1
            except Exception as e:
                print(f"Error guardando endpoint: {e}")
        
        db.commit()
        
        return {
            "message": f"Descubiertos {len(discovered_endpoints)} endpoints, guardados {saved_count}",
            "discovered": discovered_endpoints,
            "saved_count": saved_count
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en descubrimiento: {str(e)}")

@router.get("/stats")
async def discovery_stats(db: Session = Depends(get_db)):
    """Estadísticas de descubrimiento"""
    total_endpoints = db.query(APIEndpoint).count()
    discovered_endpoints = db.query(APIEndpoint).filter(
        APIEndpoint.description.like("%Descubierto automáticamente%")
    ).count()
    
    return {
        "total_endpoints": total_endpoints,
        "discovered_endpoints": discovered_endpoints,
        "manual_endpoints": total_endpoints - discovered_endpoints
    }
