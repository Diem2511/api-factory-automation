from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.services.dashboard_service import DashboardService
from app.models import get_db, APIEndpoint, WrapperConfig, APIService
import json

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/", response_class=HTMLResponse)
async def get_dashboard():
    """Devuelve el HTML del dashboard (en una implementación real sería un archivo estático)"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>API Factory Dashboard</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; }
            .header { background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
            .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 20px; }
            .stat-card { background: white; padding: 20px; border-radius: 8px; text-align: center; }
            .quick-actions { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; }
            .action-card { background: white; padding: 20px; border-radius: 8px; cursor: pointer; }
            .action-card:hover { box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚀 API Factory Automation</h1>
                <p>Sistema automatizado para descubrir, envolver y desplegar APIs</p>
            </div>
            
            <div id="stats" class="stats">
                <!-- Las estadísticas se cargarán via JavaScript -->
            </div>
            
            <div class="quick-actions" id="quick-actions">
                <!-- Las acciones se cargarán via JavaScript -->
            </div>
            
            <div id="recent-activity">
                <!-- Actividad reciente -->
            </div>
        </div>
        
        <script>
            // Cargar datos del dashboard
            async function loadDashboard() {
                try {
                    const response = await fetch('/dashboard/data');
                    const data = await response.json();
                    
                    // Actualizar estadísticas
                    document.getElementById('stats').innerHTML = data.stats_html;
                    
                    // Actualizar acciones rápidas
                    document.getElementById('quick-actions').innerHTML = data.actions_html;
                    
                } catch (error) {
                    console.error('Error loading dashboard:', error);
                }
            }
            
            loadDashboard();
        </script>
    </body>
    </html>
    """

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
        active_deployments = db.query(WrapperConfig).filter(
            WrapperConfig.config.contains({"deployments": [{"status": "deployed"}]})
        ).count()
        
        stats = {
            "total_endpoints": total_endpoints,
            "discovered_endpoints": discovered_endpoints,
            "wrappers_count": wrappers_count,
            "active_deployments": active_deployments
        }
        
        dashboard_data = dashboard_service.generate_dashboard_data(stats)
        
        # Generar HTML para las estadísticas
        stats_html = f'''
        <div class="stat-card">
            <h3>📊 Endpoints</h3>
            <p style="font-size: 2em; margin: 10px 0;">{stats["total_endpoints"]}</p>
            <small>{stats["discovered_endpoints"]} descubiertos</small>
        </div>
        <div class="stat-card">
            <h3>🛠️ Wrappers</h3>
            <p style="font-size: 2em; margin: 10px 0;">{stats["wrappers_count"]}</p>
            <small>generados</small>
        </div>
        <div class="stat-card">
            <h3>🚀 Despliegues</h3>
            <p style="font-size: 2em; margin: 10px 0;">{stats["active_deployments"]}</p>
            <small>activos</small>
        </div>
        <div class="stat-card">
            <h3>✅ Estado</h3>
            <p style="font-size: 2em; margin: 10px 0;">🟢</p>
            <small>Sistema operativo</small>
        </div>
        '''
        
        # Generar HTML para acciones rápidas
        actions_html = ""
        for action in dashboard_data["quick_actions"]:
            actions_html += f'''
            <div class="action-card" onclick="executeAction('{action["endpoint"]}', '{action["method"]}')">
                <h3>{action["icon"]} {action["title"]}</h3>
                <p>{action["description"]}</p>
            </div>
            '''
        
        return {
            "overview": dashboard_data["overview"],
            "recent_activity": dashboard_data["recent_activity"],
            "system_stats": dashboard_data["system_stats"],
            "stats_html": stats_html,
            "actions_html": actions_html
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading dashboard: {str(e)}")

@router.get("/discovery")
async def get_discovery_interface(url: str = None, db: Session = Depends(get_db)):
    """Interfaz para descubrimiento de APIs"""
    dashboard_service = DashboardService()
    
    # Si se proporciona una URL, simular descubrimiento
    discovery_results = {}
    if url:
        # En una implementación real, llamaríamos al servicio de descubrimiento
        discovery_results = {
            "url": url,
            "discovered": [],
            "saved_count": 0
        }
    
    ui_data = dashboard_service.generate_discovery_ui(discovery_results)
    
    return {
        "interface": "discovery",
        "data": ui_data,
        "form_config": {
            "fields": [
                {
                    "name": "url",
                    "type": "url",
                    "label": "URL a analizar",
                    "placeholder": "https://ejemplo.com",
                    "required": True
                }
            ],
            "submit_endpoint": "/discovery/discover",
            "method": "POST"
        }
    }

@router.get("/wrappers/{wrapper_id}/interface")
async def get_wrapper_interface(wrapper_id: int, db: Session = Depends(get_db)):
    """Interfaz para gestión de wrappers"""
    wrapper_config = db.query(WrapperConfig).filter(WrapperConfig.id == wrapper_id).first()
    if not wrapper_config:
        raise HTTPException(status_code=404, detail="Wrapper no encontrado")
    
    dashboard_service = DashboardService()
    
    wrapper_data = {
        "id": wrapper_config.id,
        "name": wrapper_config.name,
        "wrapper_type": wrapper_config.wrapper_type,
        "endpoints_count": len(wrapper_config.config.get("endpoints", [])) if wrapper_config.config else 0,
        "wrapper_code": "# Código del wrapper...",  # En realidad vendría de la base de datos
        "endpoints": wrapper_config.config.get("endpoints", []) if wrapper_config.config else []
    }
    
    ui_data = dashboard_service.generate_wrapper_ui(wrapper_data)
    
    return {
        "interface": "wrapper",
        "wrapper_id": wrapper_id,
        "data": ui_data
    }

@router.get("/deployment/{wrapper_id}/interface")
async def get_deployment_interface(wrapper_id: int, db: Session = Depends(get_db)):
    """Interfaz para despliegue de wrappers"""
    wrapper_config = db.query(WrapperConfig).filter(WrapperConfig.id == wrapper_id).first()
    if not wrapper_config:
        raise HTTPException(status_code=404, detail="Wrapper no encontrado")
    
    dashboard_service = DashboardService()
    
    # Obtener información de despliegue
    deployments = wrapper_config.config.get("deployments", []) if wrapper_config.config else []
    latest_deployment = deployments[-1] if deployments else {}
    
    deployment_data = {
        "status": latest_deployment.get("status", "not_deployed"),
        "platform": latest_deployment.get("platform", ""),
        "urls": [latest_deployment.get("url", "")] if latest_deployment.get("url") else [],
        "next_steps": [
            "Configurar variables de entorno",
            "Probar endpoints desplegados",
            "Configurar monitoreo"
        ]
    }
    
    ui_data = dashboard_service.generate_deployment_ui(deployment_data)
    
    return {
        "interface": "deployment",
        "wrapper_id": wrapper_id,
        "data": ui_data,
        "deployment_options": [
            {"platform": "fastapi", "name": "FastAPI Standalone"},
            {"platform": "vercel", "name": "Vercel"},
            {"platform": "railway", "name": "Railway"}
        ]
    }

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
