#!/usr/bin/env python3
import requests
import json
import os
import re
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.api_opportunity import ApiOpportunity

class AutoWrapperGenerator:
    def __init__(self):
        self.deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
        self.base_url = "https://api.deepseek.com/v1"
        
    def generate_wrapper(self, api_opportunity):
        """Genera un wrapper de API usando DeepSeek"""
        print(f"🛠️ Generando wrapper para: {api_opportunity.name}")
        
        prompt = f"""
        Eres un experto desarrollador de APIs. Crea un wrapper de FastAPI para la siguiente API:
        
        Nombre: {api_opportunity.name}
        Descripción: {api_opportunity.description}
        URL: {api_opportunity.source_url}
        
        Requisitos:
        1. Crea un wrapper completo de FastAPI
        2. Incluye endpoints RESTful estándar
        3. Manejo de errores robusto
        4. Documentación automática con Swagger
        5. Rate limiting básico
        6. Cache con Redis
        7. Logging apropiado
        
        Genera el código Python completo listo para usar.
        """
        
        try:
            headers = {
                "Authorization": f"Bearer {self.deepseek_api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "deepseek-coder",
                "messages": [
                    {"role": "system", "content": "Eres un experto desarrollador de Python y FastAPI."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 4000,
                "temperature": 0.3
            }
            
            response = requests.post(f"{self.base_url}/chat/completions", 
                                   headers=headers, json=data, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                wrapper_code = result['choices'][0]['message']['content']
                
                # Extraer solo el código Python
                python_code = self.extract_python_code(wrapper_code)
                
                if python_code:
                    self.save_wrapper(api_opportunity, python_code)
                    return True
                else:
                    print("❌ No se pudo extraer código Python válido")
                    return False
            else:
                print(f"❌ Error en API DeepSeek: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error generando wrapper: {e}")
            return False
    
    def extract_python_code(self, text):
        """Extrae código Python del texto generado"""
        # Buscar bloques de código entre ```
        code_blocks = re.findall(r'```python\n(.*?)\n```', text, re.DOTALL)
        if code_blocks:
            return code_blocks[0]
        
        # Si no encuentra bloques, buscar código directamente
        lines = text.split('\n')
        python_lines = []
        in_code = False
        
        for line in lines:
            if line.strip().startswith('```'):
                in_code = not in_code
                continue
            if in_code or (line.strip() and not line.startswith('#')):
                python_lines.append(line)
        
        return '\n'.join(python_lines) if python_lines else text
    
    def save_wrapper(self, opportunity, code):
        """Guarda el wrapper generado"""
        safe_name = re.sub(r'[^a-zA-Z0-9]', '_', opportunity.name.lower())
        filename = f"generated_wrappers/{safe_name}_api.py"
        
        os.makedirs("generated_wrappers", exist_ok=True)
        
        with open(filename, 'w') as f:
            f.write(code)
        
        print(f"✅ Wrapper guardado en: {filename}")
        
        # Actualizar base de datos
        db = SessionLocal()
        try:
            opportunity.is_processed = True
            db.commit()
        except Exception as e:
            db.rollback()
            print(f"❌ Error actualizando BD: {e}")
        finally:
            db.close()

def process_pending_opportunities():
    """Procesa oportunidades pendientes de la base de datos"""
    db = SessionLocal()
    try:
        opportunities = db.query(ApiOpportunity).filter(
            ApiOpportunity.is_processed == False,
            ApiOpportunity.viability_score >= 6.0
        ).limit(3).all()
        
        generator = AutoWrapperGenerator()
        success_count = 0
        
        for opportunity in opportunities:
            if generator.generate_wrapper(opportunity):
                success_count += 1
                
        print(f"🎉 Wrappers generados exitosamente: {success_count}/{len(opportunities)}")
        
    except Exception as e:
        print(f"❌ Error procesando oportunidades: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    process_pending_opportunities()
