import requests
import json
import inspect
from typing import Dict, Any, List
from fastapi import HTTPException

class APIWrapperService:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'APIFactoryWrapper/1.0',
            'Content-Type': 'application/json'
        })
    
    def create_rest_wrapper(self, base_url: str, endpoints: List[Dict]) -> Dict[str, Any]:
        """Crea un wrapper REST para una API"""
        wrapper_code = self._generate_rest_wrapper_code(base_url, endpoints)
        config = self._generate_wrapper_config(base_url, endpoints, 'rest')
        
        return {
            "wrapper_type": "rest",
            "base_url": base_url,
            "endpoints_wrapped": len(endpoints),
            "wrapper_code": wrapper_code,
            "config": config
        }
    
    def create_graphql_wrapper(self, endpoint_url: str, schema: Dict = None) -> Dict[str, Any]:
        """Crea un wrapper GraphQL"""
        wrapper_code = self._generate_graphql_wrapper_code(endpoint_url)
        config = self._generate_graphql_config(endpoint_url, schema)
        
        return {
            "wrapper_type": "graphql",
            "endpoint_url": endpoint_url,
            "wrapper_code": wrapper_code,
            "config": config
        }
    
    def _generate_rest_wrapper_code(self, base_url: str, endpoints: List[Dict]) -> str:
        """Genera código Python para wrapper REST"""
        methods = []
        
        for endpoint in endpoints:
            method_name = self._generate_method_name(endpoint['url'], endpoint['method'])
            method_code = self._generate_method_code(endpoint, base_url)
            methods.append(method_code)
        
        wrapper_class = f'''
class APIWrapper:
    def __init__(self, base_url="{base_url}", api_key=None):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        if api_key:
            self.session.headers.update({{'Authorization': f'Bearer {{api_key}}'}})
    
    {"".join(methods)}
    
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
'''
        return f"import requests\n\n{wrapper_class}"
    
    def _generate_method_name(self, url: str, method: str) -> str:
        """Genera un nombre de método legible a partir de la URL"""
        # Extraer partes significativas de la URL
        parts = url.strip('/').split('/')
        meaningful_parts = [p for p in parts if not p.startswith('{') and p not in ['api', 'v1', 'v2']]
        
        if meaningful_parts:
            base_name = '_'.join(meaningful_parts[-2:])  # Usar las últimas 2 partes
        else:
            base_name = 'endpoint'
        
        # Limpiar el nombre
        base_name = ''.join(c if c.isalnum() else '_' for c in base_name)
        base_name = base_name.strip('_')
        
        # Añadir prefijo según el método
        method_prefix = {
            'GET': 'get_',
            'POST': 'create_',
            'PUT': 'update_',
            'DELETE': 'delete_',
            'PATCH': 'patch_'
        }.get(method.upper(), 'call_')
        
        return f"{method_prefix}{base_name}"
    
    def _generate_method_code(self, endpoint: Dict, base_url: str) -> str:
        """Genera código para un método específico"""
        method_name = self._generate_method_name(endpoint['url'], endpoint['method'])
        
        # Extraer parámetros de la URL
        url_parts = endpoint['url'].split('/')
        path_params = [part[1:-1] for part in url_parts if part.startswith('{') and part.endswith('}')]
        
        param_list = ["self"]
        if path_params:
            param_list.extend(path_params)
        
        # Añadir parámetros de query para GET
        if endpoint['method'].upper() == 'GET':
            param_list.append("query_params=None")
        
        # Añadir data para POST/PUT
        if endpoint['method'].upper() in ['POST', 'PUT', 'PATCH']:
            param_list.append("data=None")
        
        params_str = ", ".join(param_list)
        
        # Construir la URL
        endpoint_url = endpoint['url']
        if path_params:
            url_builder = f'endpoint = f"{endpoint_url}"'
        else:
            url_builder = f'endpoint = "{endpoint_url}"'
        
        method_code = f'''
    def {method_name}({params_str}):
        """{endpoint.get('description', 'Auto-generated endpoint')}"""
        {url_builder}
        return self._make_request("{endpoint['method']}", endpoint{', params=query_params' if 'query_params' in param_list else ''}{', data=data' if 'data' in param_list else ''})
'''
        return method_code
    
    def _generate_wrapper_config(self, base_url: str, endpoints: List[Dict], wrapper_type: str) -> Dict:
        """Genera configuración para el wrapper"""
        return {
            "base_url": base_url,
            "wrapper_type": wrapper_type,
            "endpoints": [
                {
                    "url": endpoint['url'],
                    "method": endpoint['method'],
                    "wrapper_method": self._generate_method_name(endpoint['url'], endpoint['method']),
                    "parameters": self._extract_parameters(endpoint['url'])
                }
                for endpoint in endpoints
            ],
            "authentication": {
                "type": "api_key",
                "location": "header"
            }
        }
    
    def _extract_parameters(self, url: str) -> List[str]:
        """Extrae parámetros de la URL"""
        import re
        return re.findall(r'\{(\w+)\}', url)
    
    def _generate_graphql_wrapper_code(self, endpoint_url: str) -> str:
        """Genera código para wrapper GraphQL"""
        return f'''
import requests

class GraphQLWrapper:
    def __init__(self, endpoint_url="{endpoint_url}", api_key=None):
        self.endpoint_url = endpoint_url
        self.session = requests.Session()
        if api_key:
            self.session.headers.update({{'Authorization': f'Bearer {{api_key}}'}})
    
    def query(self, query_string, variables=None):
        """Ejecuta una query GraphQL"""
        payload = {{
            "query": query_string,
            "variables": variables or {{}}
        }}
        
        try:
            response = self.session.post(
                self.endpoint_url,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"GraphQL query error: {{e}}")
            raise
    
    def mutation(self, mutation_string, variables=None):
        """Ejecuta una mutation GraphQL"""
        return self.query(mutation_string, variables)
'''
    
    def _generate_graphql_config(self, endpoint_url: str, schema: Dict = None) -> Dict:
        """Genera configuración para wrapper GraphQL"""
        return {
            "endpoint_url": endpoint_url,
            "wrapper_type": "graphql",
            "operations": ["query", "mutation"],
            "schema_available": schema is not None
        }

# Ejemplo de uso
if __name__ == "__main__":
    wrapper_service = APIWrapperService()
    
    # Ejemplo con endpoints REST
    endpoints = [
        {"url": "/users", "method": "GET", "description": "Get all users"},
        {"url": "/users/{id}", "method": "GET", "description": "Get user by ID"},
        {"url": "/users", "method": "POST", "description": "Create new user"}
    ]
    
    result = wrapper_service.create_rest_wrapper("https://api.example.com", endpoints)
    print("Wrapper REST generado:")
    print(result["wrapper_code"])
