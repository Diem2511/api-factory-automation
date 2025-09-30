import requests
from bs4 import BeautifulSoup
import re
import json
from typing import List, Dict

class APIDiscoveryService:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; APIFactoryBot/1.0)'
        })
    
    def discover_from_webpage(self, url: str) -> List[Dict]:
        """Descubre endpoints API desde una página web"""
        try:
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            endpoints = []
            
            # Buscar enlaces que puedan ser endpoints API
            for link in soup.find_all('a', href=True):
                href = link['href']
                if self._looks_like_api_endpoint(href):
                    endpoints.append({
                        'url': href,
                        'method': self._guess_method(href),
                        'source': 'webpage_link'
                    })
            
            # Buscar en scripts JavaScript
            for script in soup.find_all('script'):
                if script.string:
                    endpoints.extend(self._find_in_javascript(script.string))
            
            return endpoints
            
        except Exception as e:
            print(f"Error descubriendo APIs: {e}")
            return []
    
    def _looks_like_api_endpoint(self, url: str) -> bool:
        """Determina si una URL parece ser un endpoint API"""
        api_patterns = [
            r'/api/',
            r'/v[0-9]+/',
            r'\.json$',
            r'\.xml$',
            r'graphql',
            r'rest',
        ]
        return any(re.search(pattern, url, re.IGNORECASE) for pattern in api_patterns)
    
    def _guess_method(self, url: str) -> str:
        """Intenta adivinar el método HTTP basado en la URL"""
        if re.search(r'(get|fetch|query)', url, re.IGNORECASE):
            return 'GET'
        elif re.search(r'(post|create|submit)', url, re.IGNORECASE):
            return 'POST'
        elif re.search(r'(put|update)', url, re.IGNORECASE):
            return 'PUT'
        elif re.search(r'(delete|remove)', url, re.IGNORECASE):
            return 'DELETE'
        else:
            return 'GET'
    
    def _find_in_javascript(self, js_code: str) -> List[Dict]:
        """Busca endpoints API en código JavaScript"""
        endpoints = []
        
        # Patrones comunes en JavaScript
        patterns = [
            r'fetch\(["\']([^"\']+)["\']',
            r'axios\.(get|post|put|delete)\(["\']([^"\']+)["\']',
            r'\.ajax\([^)]*url:\s*["\']([^"\']+)["\']',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, js_code)
            for match in matches:
                url = match.group(1) if len(match.groups()) > 1 else match.group(0)
                if self._looks_like_api_endpoint(url):
                    endpoints.append({
                        'url': url,
                        'method': self._guess_method(url),
                        'source': 'javascript'
                    })
        
        return endpoints

# Ejemplo de uso
if __name__ == "__main__":
    discovery = APIDiscoveryService()
    endpoints = discovery.discover_from_webpage("https://jsonplaceholder.typicode.com")
    print(f"Endpoints descubiertos: {len(endpoints)}")
    for endpoint in endpoints[:5]:
        print(f"- {endpoint['method']} {endpoint['url']}")
