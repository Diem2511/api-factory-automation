from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.services.deployment_service import DeploymentService
from app.models import get_db, WrapperConfig
import json

router = APIRouter(prefix="/deployment", tags=["deployment"])

@router.post("/deploy/{wrapper_id}")
async def deploy_wrapper(
    wrapper_id: int,
    platform: str = "fastapi",  # fastapi, vercel, railway
    project_name: str = None,
    db: Session = Depends(get_db)
):
    """Despliega un wrapper generado a una plataforma"""
    try:
        # Obtener configuración del wrapper
        wrapper_config = db.query(WrapperConfig).filter(WrapperConfig.id == wrapper_id).first()
        if not wrapper_config:
            raise HTTPException(status_code=404, detail="Wrapper no encontrado")
        
        # En una implementación real, obtendríamos el código del wrapper de la base de datos
        # Por ahora generamos código basado en la configuración
        deployment_service = DeploymentService()
        
        # Generar código de ejemplo basado en la configuración
        wrapper_code = _generate_wrapper_code_from_config(wrapper_config)
        
        # Generar nombre de proyecto si no se proporciona
        if not project_name:
            project_name = f"api-wrapper-{wrapper_id}"
        
        # Desplegar según la plataforma
        if platform == "vercel":
            result = deployment_service.deploy_to_vercel(wrapper_code, project_name)
        elif platform == "railway":
            result = deployment_service.deploy_to_railway(wrapper_code, project_name)
        elif platform == "fastapi":
            result = deployment_service.deploy_as_fastapi(wrapper_code, project_name)
        else:
            raise HTTPException(status_code=400, detail="Plataforma no soportada")
        
        # Actualizar configuración del wrapper con info de despliegue
        if wrapper_config.config:
            config = wrapper_config.config
        else:
            config = {}
        
        if "deployments" not in config:
            config["deployments"] = []
        
        config["deployments"].append({
            "platform": platform,
            "project_name": project_name,
            "status": result.get("status"),
            "timestamp": "now"  # En realidad sería datetime.now().isoformat()
        })
        
        wrapper_config.config = config
        db.commit()
        
        return {
            "message": f"Wrapper desplegado en {platform}",
            "wrapper_id": wrapper_id,
            "deployment_info": result,
            "next_steps": _get_deployment_next_steps(platform, result)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en despliegue: {str(e)}")

@router.get("/platforms")
async def list_deployment_platforms():
    """Lista las plataformas de despliegue disponibles"""
    return {
        "platforms": [
            {
                "name": "fastapi",
                "description": "App FastAPI independiente",
                "requirements": ["Python 3.8+", "Requirements.txt"],
                "best_for": "APIs complejas, máximo control"
            },
            {
                "name": "vercel", 
                "description": "Funciones serverless en Vercel",
                "requirements": ["Vercel account", "Vercel token"],
                "best_for": "Despliegue rápido, escalado automático"
            },
            {
                "name": "railway",
                "description": "Contenedores en Railway", 
                "requirements": ["Railway account", "Railway token"],
                "best_for": "Aplicaciones completas, base de datos incluida"
            }
        ]
    }

@router.get("/status/{wrapper_id}")
async def deployment_status(wrapper_id: int, db: Session = Depends(get_db)):
    """Obtiene el estado de despliegue de un wrapper"""
    wrapper_config = db.query(WrapperConfig).filter(WrapperConfig.id == wrapper_id).first()
    if not wrapper_config:
        raise HTTPException(status_code=404, detail="Wrapper no encontrado")
    
    deployments = wrapper_config.config.get("deployments", []) if wrapper_config.config else []
    
    return {
        "wrapper_id": wrapper_id,
        "wrapper_name": wrapper_config.name,
        "deployments": deployments,
        "active_deployments": [d for d in deployments if d.get("status") == "deployed"]
    }

@router.post("/generate-package/{wrapper_id}")
async def generate_deployment_package(wrapper_id: int, db: Session = Depends(get_db)):
    """Genera un paquete de despliegue descargable"""
    wrapper_config = db.query(WrapperConfig).filter(WrapperConfig.id == wrapper_id).first()
    if not wrapper_config:
        raise HTTPException(status_code=404, detail="Wrapper no encontrado")
    
    deployment_service = DeploymentService()
    wrapper_code = _generate_wrapper_code_from_config(wrapper_config)
    project_name = f"api-wrapper-{wrapper_id}"
    
    package = deployment_service.deploy_as_fastapi(wrapper_code, project_name)
    
    return {
        "wrapper_id": wrapper_id,
        "project_name": project_name,
        "files": package.get("deployment_package", {}),
        "instructions": package.get("instructions", [])
    }

def _generate_wrapper_code_from_config(wrapper_config) -> str:
    """Genera código de wrapper basado en la configuración (simulado)"""
    # En una implementación real, esto vendría de la base de datos
    # Por ahora generamos código de ejemplo
    
    base_url = wrapper_config.config.get("base_url", "https://api.example.com") if wrapper_config.config else "https://api.example.com"
    
    return f'''
import requests

class APIWrapper:
    def __init__(self, base_url="{base_url}", api_key=None):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        if api_key:
            self.session.headers.update({{'Authorization': f'Bearer {{api_key}}'}})
    
    def _make_request(self, method, endpoint, params=None, data=None):
        url = f"{{self.base_url}}{{endpoint}}"
        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=data,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error calling {{url}}: {{e}}")
            raise

    # Métodos de ejemplo basados en endpoints comunes
    def get_users(self, query_params=None):
        """Obtener lista de usuarios"""
        return self._make_request("GET", "/users", params=query_params)
    
    def get_user(self, user_id):
        """Obtener usuario por ID"""
        return self._make_request("GET", f"/users/{{user_id}}")
    
    def create_user(self, data=None):
        """Crear nuevo usuario"""
        return self._make_request("POST", "/users", data=data)
'''

def _get_deployment_next_steps(platform: str, result: dict) -> list:
    """Genera pasos siguientes basados en la plataforma"""
    base_steps = [
        "Guarda las URLs y credenciales proporcionadas",
        "Prueba los endpoints desplegados",
        "Configura monitoring y alertas"
    ]
    
    if platform == "vercel":
        return [
            "Tu API está disponible en: " + result.get("url", "N/A"),
            "Puedes configurar un dominio personalizado en Vercel",
            "Revisa los logs en el dashboard de Vercel"
        ] + base_steps
    
    elif platform == "railway":
        return [
            "Tu app está desplegada en Railway",
            "Puedes conectar una base de datos desde el dashboard",
            "Revisa las variables de entorno en Railway"
        ] + base_steps
    
    else:  # fastapi
        return [
            "Descarga el paquete generado",
            "Sigue las instrucciones de despliegue",
            "Personaliza la app según tus necesidades"
        ] + base_steps
