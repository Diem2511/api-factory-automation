#!/usr/bin/env python3
import os
import subprocess
import requests
import time
from pathlib import Path

class AutoDeployer:
    def __init__(self):
        self.deployed_apis = []
        
    def deploy_to_railway(self, wrapper_path):
        """Despliega un wrapper a Railway"""
        print(f"🚀 Desplegando {wrapper_path} a Railway...")
        
        try:
            # Crear estructura temporal para deployment
            temp_dir = f"deploy_{int(time.time())}"
            os.makedirs(temp_dir, exist_ok=True)
            
            # Copiar archivos necesarios
            self.create_deployment_structure(temp_dir, wrapper_path)
            
            # Usar Railway CLI para deployment
            result = subprocess.run([
                'railway', 'deploy', '--service', temp_dir
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print(f"✅ Deployment exitoso para {wrapper_path}")
                return True
            else:
                print(f"❌ Error en deployment: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error desplegando a Railway: {e}")
            return False
    
    def create_deployment_structure(self, temp_dir, wrapper_path):
        """Crea estructura para deployment"""
        # requirements.txt
        with open(f"{temp_dir}/requirements.txt", 'w') as f:
            f.write("""
fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
requests==2.31.0
redis==5.0.1
celery==5.3.4
            """.strip())
        
        # main.py adaptado
        wrapper_content = Path(wrapper_path).read_text()
        with open(f"{temp_dir}/main.py", 'w') as f:
            f.write(wrapper_content)
        
        # railway.json
        with open(f"{temp_dir}/railway.json", 'w') as f:
            f.write("""
{
    "$schema": "https://railway.app/railway.schema.json",
    "build": {
        "builder": "NIXPACKS"
    },
    "deploy": {
        "startCommand": "uvicorn main:app --host 0.0.0.0 --port $PORT"
    }
}
            """.strip())

def main():
    deployer = AutoDeployer()
    
    # Buscar wrappers generados
    wrapper_dir = Path("generated_wrappers")
    if wrapper_dir.exists():
        wrapper_files = list(wrapper_dir.glob("*.py"))
        
        for wrapper_file in wrapper_files[:2]:  # Desplegar primeros 2
            deployer.deploy_to_railway(str(wrapper_file))
            time.sleep(10)  # Esperar entre deployments
    else:
        print("❌ No hay wrappers generados para desplegar")

if __name__ == "__main__":
    main()
