from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from app.services.dashboard_service import DashboardService
from app.models import get_db, APIEndpoint, WrapperConfig, APIService
import os

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

# Servir archivos estáticos
@router.get("/", response_class=HTMLResponse)
async def get_dashboard():
    """Devuelve el dashboard principal"""
    return FileResponse('static/index.html')

@router.get("/data")
async def get_dashboard_data(db: Session = Depends(get_db)):
    """Devuelve datos para el dashboard"""
    try:
        dashboard_service = DashboardService()
        
        # Obtener estadísticas reales de la base de datos
        total_endpoints = db.query(APIEndpoint).count()
        discovered_endpoints = db.query(APIEndpoint).filter(
            APIEndpoint.description.like("%Descubierto automáticamente%")
        ).count()
        wrappers_count = db.query(WrapperConfig).count()
        
        # Contar despliegues activos (simulado por ahora)
        active_deployments = db.query(WrapperConfig).filter(
            WrapperConfig.is_active == True
        ).count()

        stats = {
            "total_endpoints": total_endpoints,
            "discovered_endpoints": discovered_endpoints,
            "wrappers_count": wrappers_count,
            "active_deployments": active_deployments
        }
        
        dashboard_data = dashboard_service.generate_dashboard_data(stats)
        
        return dashboard_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading dashboard: {str(e)}")

@router.get("/analytics")
async def get_analytics_dashboard(db: Session = Depends(get_db)):
    """Dashboard de analíticas"""
    # Estadísticas básicas
    total_endpoints = db.query(APIEndpoint).count()
    total_wrappers = db.query(WrapperConfig).count()
    total_services = db.query(APIService).count()
    
    # Endpoints por método HTTP
    methods_count = {
        "GET": db.query(APIEndpoint).filter(APIEndpoint.method == "GET").count(),
        "POST": db.query(APIEndpoint).filter(APIEndpoint.method == "POST").count(),
        "PUT": db.query(APIEndpoint).filter(APIEndpoint.method == "PUT").count(),
        "DELETE": db.query(APIEndpoint).filter(APIEndpoint.method == "DELETE").count()
    }
    
    return {
        "overview": {
            "total_endpoints": total_endpoints,
            "total_wrappers": total_wrappers,
            "total_services": total_services,
            "success_rate": "95%"
        },
        "method_distribution": methods_count,
        "growth_metrics": {
            "endpoints_this_week": total_endpoints,
            "wrappers_this_week": total_wrappers,
            "deployments_this_week": 0
        },
        "popular_endpoints": [
            {"url": "/users", "method": "GET", "usage_count": 150},
            {"url": "/products", "method": "GET", "usage_count": 120},
            {"url": "/orders", "method": "POST", "usage_count": 80}
        ]
    }
