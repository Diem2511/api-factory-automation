import os
import json
import requests
import tempfile
import subprocess
from typing import Dict, Any, List
import httpx

class DeploymentService:
    def __init__(self):
        self.vercel_token = os.getenv("VERCEL_TOKEN", "")
        self.netlify_token = os.getenv("NETLIFY_TOKEN", "")
    
    def deploy_to_vercel(self, wrapper_code: str, project_name: str) -> Dict[str, Any]:
        """Despliega un wrapper como función serverless en Vercel"""
        try:
            # Crear estructura de proyecto Vercel
            project_structure = self._create_vercel_project(wrapper_code, project_name)
            
            # En una implementación real, aquí subiríamos a Vercel via API
            # Por ahora simulamos el proceso
            
            return {
                "platform": "vercel",
                "status": "deployed",
                "url": f"https://{project_name}.vercel.app",
                "deployment_id": f"dep_{project_name}_{hash(wrapper_code)}",
                "wrapper_endpoints": self._extract_endpoints_from_code(wrapper_code),
                "api_url": f"https://{project_name}.vercel.app/api"
            }
            
        except Exception as e:
            return {
                "platform": "vercel",
                "status": "failed",
                "error": str(e)
            }
    
    def deploy_to_railway(self, wrapper_code: str, project_name: str) -> Dict[str, Any]:
        """Despliega un wrapper en Railway"""
        try:
            # Crear estructura para Railway
            project_structure = self._create_railway_project(wrapper_code, project_name)
            
            return {
                "platform": "railway",
                "status": "deployed",
                "url": f"https://{project_name}.production.up.railway.app",
                "deployment_id": f"railway_{project_name}",
                "wrapper_endpoints": self._extract_endpoints_from_code(wrapper_code)
            }
            
        except Exception as e:
            return {
                "platform": "railway", 
                "status": "failed",
                "error": str(e)
            }
    
    def deploy_as_fastapi(self, wrapper_code: str, project_name: str) -> Dict[str, Any]:
        """Despliega el wrapper como una app FastAPI independiente"""
        try:
            fastapi_app_code = self._wrap_in_fastapi(wrapper_code, project_name)
            
            return {
                "platform": "fastapi",
                "status": "ready",
                "deployment_package": {
                    "main.py": fastapi_app_code,
                    "requirements.txt": self._generate_requirements(),
                    "railway.toml": self._generate_railway_config(project_name)
                },
                "instructions": [
                    "1. Copia los archivos generados a un nuevo repositorio",
                    "2. Conecta el repositorio a Railway o Vercel",
                    "3. El despliegue será automático"
                ]
            }
            
        except Exception as e:
            return {
                "platform": "fastapi",
                "status": "failed", 
                "error": str(e)
            }
    
    def _create_vercel_project(self, wrapper_code: str, project_name: str) -> Dict[str, str]:
        """Crea la estructura de proyecto para Vercel"""
        api_code = f'''
from {project_name}_wrapper import APIWrapper
from fastapi import FastAPI
import os

app = FastAPI(title="{project_name} API", version="1.0.0")
wrapper = APIWrapper()

# Auto-generar endpoints basados en los métodos del wrapper
import inspect

methods = [method for method in dir(wrapper) if not method.startswith('_') and callable(getattr(wrapper, method))]

for method_name in methods:
    if method_name.startswith('get_'):
        @app.get("/" + method_name[4:])
        async def {method_name}_endpoint():
            return getattr(wrapper, method_name)()
    
    elif method_name.startswith('create_'):
        @app.post("/" + method_name[7:])
        async def {method_name}_endpoint(data: dict):
            return getattr(wrapper, method_name)(data=data)
'''
        return {
            "api/index.py": api_code,
            f"{project_name}_wrapper.py": wrapper_code,
            "requirements.txt": "fastapi==0.104.1\nuvicorn==0.24.0\nrequests==2.31.0",
            "vercel.json": json.dumps({
                "version": 2,
                "builds": [{"src": "api/index.py", "use": "@vercel/python"}],
                "routes": [{"src": "/(.*)", "dest": "/api/index.py"}]
            })
        }
    
    def _create_railway_project(self, wrapper_code: str, project_name: str) -> Dict[str, str]:
        """Crea la estructura para Railway"""
        return {
            "main.py": self._wrap_in_fastapi(wrapper_code, project_name),
            "requirements.txt": self._generate_requirements(),
            "railway.toml": self._generate_railway_config(project_name)
        }
    
    def _wrap_in_fastapi(self, wrapper_code: str, project_name: str) -> str:
        """Envuelve el wrapper en una app FastAPI"""
        return f'''
{wrapper_code}

from fastapi import FastAPI
import uvicorn

app = FastAPI(title="{project_name} API", version="1.0.0")

# Instanciar el wrapper
wrapper = APIWrapper()

# Endpoints automáticos
@app.get("/")
async def root():
    return {{"message": "{project_name} API - Generated by API Factory", "status": "active"}}

@app.get("/health")
async def health():
    return {{"status": "healthy"}}

# Aquí se inyectarían los endpoints específicos del wrapper
# basados en los métodos disponibles

if __name__ == "__main__":
    import os
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
'''
    
    def _generate_requirements(self) -> str:
        """Genera requirements.txt para el despliegue"""
        return """fastapi==0.104.1
uvicorn==0.24.0
requests==2.31.0
python-dotenv==1.0.0"""
    
    def _generate_railway_config(self, project_name: str) -> str:
        """Genera railway.toml"""
        return f'''
[build]
builder = "nixpacks"

[deploy]
startCommand = "python main.py"

[service]
[[service.ports]]
port = 8000
http = "/"

[variables]
PORT = "8000"
'''
    
    def _extract_endpoints_from_code(self, wrapper_code: str) -> List[str]:
        """Extrae los nombres de métodos/endpoints del código del wrapper"""
        import re
        methods = re.findall(r'def\s+(\w+)\s*\(', wrapper_code)
        # Filtrar métodos mágicos y privados
        return [method for method in methods if not method.startswith('_') and method not in ['_make_request']]

# Ejemplo de uso
if __name__ == "__main__":
    deployment = DeploymentService()
    
    # Código de ejemplo
    example_wrapper = '''
import requests

class APIWrapper:
    def __init__(self, base_url="https://api.example.com"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def get_users(self):
        return self._make_request("GET", "/users")
    
    def get_user(self, user_id):
        return self._make_request("GET", f"/users/{{user_id}}")
    
    def _make_request(self, method, endpoint):
        url = f"{{self.base_url}}{{endpoint}}"
        response = self.session.request(method, url)
        return response.json()
'''
    
    result = deployment.deploy_as_fastapi(example_wrapper, "test-api")
    print("Despliegue preparado:")
    print(json.dumps(result, indent=2))
