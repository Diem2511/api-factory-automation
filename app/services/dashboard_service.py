from typing import Dict, List, Any
import json
from datetime import datetime

class DashboardService:
    def __init__(self):
        self.default_config = {
            "theme": "light",
            "language": "es",
            "auto_refresh": True
        }
    
    def generate_dashboard_data(self, stats: Dict) -> Dict[str, Any]:
        """Genera datos para el dashboard"""
        return {
            "overview": {
                "total_endpoints": stats.get("total_endpoints", 0),
                "discovered_endpoints": stats.get("discovered_endpoints", 0),
                "wrappers_generated": stats.get("wrappers_count", 0),
                "active_deployments": stats.get("active_deployments", 0),
                "system_health": "healthy"
            },
            "recent_activity": self._generate_recent_activity(),
            "quick_actions": self._get_quick_actions(),
            "system_stats": self._generate_system_stats(stats)
        }
    
    def generate_discovery_ui(self, discovery_results: Dict) -> Dict[str, Any]:
        """Genera datos para la interfaz de descubrimiento"""
        return {
            "discovery_url": discovery_results.get("url", ""),
            "endpoints_found": discovery_results.get("discovered", []),
            "stats": {
                "total_found": len(discovery_results.get("discovered", [])),
                "saved_count": discovery_results.get("saved_count", 0),
                "success_rate": self._calculate_success_rate(discovery_results)
            },
            "endpoint_categories": self._categorize_endpoints(discovery_results.get("discovered", [])),
            "recommendations": self._generate_recommendations(discovery_results)
        }
    
    def generate_wrapper_ui(self, wrapper_data: Dict) -> Dict[str, Any]:
        """Genera datos para la interfaz de wrappers"""
        return {
            "wrapper_info": {
                "id": wrapper_data.get("id"),
                "name": wrapper_data.get("name", ""),
                "type": wrapper_data.get("wrapper_type", "rest"),
                "endpoints_count": wrapper_data.get("endpoints_count", 0),
                "status": wrapper_data.get("status", "generated")
            },
            "code_preview": self._format_code_preview(wrapper_data.get("wrapper_code", "")),
            "endpoints": wrapper_data.get("endpoints", []),
            "deployment_options": self._get_deployment_options(wrapper_data),
            "testing_interface": self._generate_testing_interface(wrapper_data)
        }
    
    def generate_deployment_ui(self, deployment_data: Dict) -> Dict[str, Any]:
        """Genera datos para la interfaz de despliegue"""
        return {
            "deployment_status": deployment_data.get("status", "pending"),
            "platform": deployment_data.get("platform", ""),
            "urls": deployment_data.get("urls", []),
            "deployment_logs": self._simulate_deployment_logs(),
            "next_steps": deployment_data.get("next_steps", []),
            "monitoring_links": self._generate_monitoring_links(deployment_data)
        }
    
    def _generate_recent_activity(self) -> List[Dict]:
        """Genera actividad reciente simulada"""
        return [
            {
                "id": 1,
                "type": "discovery",
                "description": "API descubierta en https://jsonplaceholder.typicode.com",
                "timestamp": datetime.now().isoformat(),
                "status": "completed"
            },
            {
                "id": 2,
                "type": "wrapper",
                "description": "Wrapper generado para JSONPlaceholder API",
                "timestamp": datetime.now().isoformat(),
                "status": "completed"
            },
            {
                "id": 3,
                "type": "deployment",
                "description": "Despliegue iniciado en Railway",
                "timestamp": datetime.now().isoformat(),
                "status": "in_progress"
            }
        ]
    
    def _get_quick_actions(self) -> List[Dict]:
        """Acciones rápidas para el dashboard"""
        return [
            {
                "id": "discover",
                "title": "Descubrir APIs",
                "description": "Analizar sitio web en busca de endpoints",
                "icon": "🔍",
                "endpoint": "/discovery/discover",
                "method": "POST"
            },
            {
                "id": "generate_wrapper",
                "title": "Generar Wrapper",
                "description": "Crear código para API descubierta",
                "icon": "🛠️",
                "endpoint": "/wrappers/generate",
                "method": "POST"
            },
            {
                "id": "deploy",
                "title": "Desplegar",
                "description": "Publicar wrapper generado",
                "icon": "🚀",
                "endpoint": "/deployment/deploy",
                "method": "POST"
            },
            {
                "id": "monitor",
                "title": "Monitorear",
                "description": "Ver estado de despliegues",
                "icon": "📊",
                "endpoint": "/deployment/status",
                "method": "GET"
            }
        ]
    
    def _generate_system_stats(self, stats: Dict) -> Dict:
        """Genera estadísticas del sistema"""
        return {
            "uptime": "99.9%",
            "response_time": "125ms",
            "memory_usage": "45%",
            "active_connections": stats.get("total_endpoints", 0) * 2,
            "throughput": f"{stats.get('wrappers_count', 0) * 10}/min"
        }
    
    def _calculate_success_rate(self, discovery_results: Dict) -> float:
        """Calcula tasa de éxito del descubrimiento"""
        total = len(discovery_results.get("discovered", []))
        saved = discovery_results.get("saved_count", 0)
        return (saved / total * 100) if total > 0 else 0
    
    def _categorize_endpoints(self, endpoints: List[Dict]) -> Dict[str, List]:
        """Categoriza endpoints por tipo"""
        categories = {
            "users": [],
            "products": [],
            "data": [],
            "system": [],
            "other": []
        }
        
        for endpoint in endpoints:
            url = endpoint.get("url", "").lower()
            
            if any(word in url for word in ['user', 'customer', 'member']):
                categories["users"].append(endpoint)
            elif any(word in url for word in ['product', 'item', 'inventory']):
                categories["products"].append(endpoint)
            elif any(word in url for word in ['data', 'analytics', 'metrics']):
                categories["data"].append(endpoint)
            elif any(word in url for word in ['health', 'status', 'system']):
                categories["system"].append(endpoint)
            else:
                categories["other"].append(endpoint)
        
        return categories
    
    def _generate_recommendations(self, discovery_results: Dict) -> List[str]:
        """Genera recomendaciones basadas en los resultados"""
        recommendations = []
        endpoints = discovery_results.get("discovered", [])
        
        if len(endpoints) == 0:
            recommendations.append("No se encontraron endpoints. Prueba con un sitio diferente.")
        
        if len(endpoints) > 10:
            recommendations.append("Se encontraron muchos endpoints. Considera filtrar por relevancia.")
        
        if any(ep.get('method') == 'POST' for ep in endpoints):
            recommendations.append("Se detectaron endpoints POST. Asegúrate de manejar autenticación.")
        
        return recommendations
    
    def _format_code_preview(self, code: str, max_lines: int = 20) -> Dict:
        """Formatea una vista previa del código"""
        lines = code.split('\n')
        preview = '\n'.join(lines[:max_lines])
        
        return {
            "preview": preview,
            "total_lines": len(lines),
            "language": "python",
            "has_more": len(lines) > max_lines
        }
    
    def _get_deployment_options(self, wrapper_data: Dict) -> List[Dict]:
        """Obtiene opciones de despliegue"""
        return [
            {
                "platform": "fastapi",
                "name": "FastAPI Standalone",
                "description": "Aplicación completa lista para desplegar",
                "icon": "🐍",
                "recommended": True,
                "requirements": ["Python 3.8+"]
            },
            {
                "platform": "vercel",
                "name": "Vercel Functions",
                "description": "Funciones serverless con escalado automático",
                "icon": "▲",
                "recommended": False,
                "requirements": ["Token de Vercel"]
            },
            {
                "platform": "railway",
                "name": "Railway",
                "description": "Contenedores con base de datos incluida",
                "icon": "🚄",
                "recommended": False,
                "requirements": ["Token de Railway"]
            }
        ]
    
    def _generate_testing_interface(self, wrapper_data: Dict) -> Dict:
        """Genera interfaz para testing de wrappers"""
        return {
            "test_endpoints": [
                {
                    "name": "get_users",
                    "method": "GET",
                    "description": "Obtener lista de usuarios",
                    "parameters": [],
                    "example_response": {"users": [], "total": 0}
                },
                {
                    "name": "get_user",
                    "method": "GET", 
                    "description": "Obtener usuario por ID",
                    "parameters": [{"name": "user_id", "type": "string", "required": True}],
                    "example_response": {"id": "1", "name": "John Doe"}
                }
            ],
            "test_environment": {
                "base_url": "https://jsonplaceholder.typicode.com",
                "timeout": 30,
                "retry_attempts": 3
            }
        }
    
    def _simulate_deployment_logs(self) -> List[str]:
        """Simula logs de despliegue"""
        return [
            "🔄 Iniciando proceso de despliegue...",
            "✅ Dependencias instaladas correctamente",
            "✅ Código verificado y compilado",
            "🚀 Subiendo a plataforma de despliegue...",
            "🌍 Configurando DNS y certificados SSL...",
            "✅ Despliegue completado exitosamente"
        ]
    
    def _generate_monitoring_links(self, deployment_data: Dict) -> List[Dict]:
        """Genera enlaces de monitoreo"""
        platform = deployment_data.get("platform", "")
        base_url = deployment_data.get("url", "")
        
        if platform == "vercel":
            return [
                {"name": "Dashboard Vercel", "url": "https://vercel.com/dashboard"},
                {"name": "Logs", "url": f"{base_url}/_logs"},
                {"name": "Métricas", "url": f"{base_url}/_metrics"}
            ]
        elif platform == "railway":
            return [
                {"name": "Dashboard Railway", "url": "https://railway.app/dashboard"},
                {"name": "Logs", "url": f"{base_url}/logs"},
                {"name": "Métricas", "url": f"{base_url}/metrics"}
            ]
        else:
            return [
                {"name": "Health Check", "url": f"{base_url}/health"},
                {"name": "Documentación", "url": f"{base_url}/docs"}
            ]

# Ejemplo de uso
if __name__ == "__main__":
    dashboard = DashboardService()
    
    # Datos de ejemplo
    stats = {
        "total_endpoints": 15,
        "discovered_endpoints": 10,
        "wrappers_count": 3,
        "active_deployments": 2
    }
    
    dashboard_data = dashboard.generate_dashboard_data(stats)
    print("Datos del dashboard:")
    print(json.dumps(dashboard_data, indent=2, ensure_ascii=False))
