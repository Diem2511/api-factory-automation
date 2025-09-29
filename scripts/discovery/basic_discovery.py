#!/usr/bin/env python3
import requests
import json
import os
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models.api_opportunity import ApiOpportunity, Base

# Crear tablas
Base.metadata.create_all(bind=engine)

class ApiDiscovery:
    def __init__(self):
        self.deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
        self.session = requests.Session()
        
    def search_github_trending(self):
        """Busca APIs trending en GitHub"""
        print("🔍 Buscando APIs trending en GitHub...")
        
        urls = [
            "https://github.com/trending?since=weekly",
            "https://github.com/topics/api",
            "https://github.com/topics/rest-api"
        ]
        
        opportunities = []
        
        for url in urls:
            try:
                response = self.session.get(url)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Buscar repositorios relacionados con APIs
                repos = soup.find_all('article', class_='Box-row')
                
                for repo in repos[:10]:
                    title_elem = repo.find('h2')
                    if title_elem:
                        title = title_elem.get_text(strip=True).replace('\n', '').replace(' ', '')
                        description_elem = repo.find('p')
                        description = description_elem.get_text(strip=True) if description_elem else ""
                        
                        if any(keyword in title.lower() or keyword in description.lower() 
                              for keyword in ['api', 'rest', 'graphql', 'wrapper', 'client']):
                            
                            opportunity = {
                                'name': title,
                                'description': description,
                                'source_url': f"https://github.com/{title}",
                                'viability_score': self.calculate_viability(description),
                                'demand_metric': self.estimate_demand(title),
                                'implementation_complexity': 3.0,
                                'category': 'github_trending',
                                'tags': 'api,github,trending'
                            }
                            opportunities.append(opportunity)
                            
            except Exception as e:
                print(f"❌ Error scraping {url}: {e}")
                
        return opportunities
    
    def search_reddit_demand(self):
        """Analiza demanda en Reddit"""
        print("🔍 Analizando demanda en Reddit...")
        
        opportunities = []
        subreddits = ['programming', 'webdev', 'learnprogramming', 'SideProject']
        
        for subreddit in subreddits:
            try:
                url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit=20"
                headers = {'User-Agent': 'API-Factory-Bot 1.0'}
                response = self.session.get(url, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    posts = data['data']['children']
                    
                    for post in posts:
                        post_data = post['data']
                        title = post_data['title']
                        selftext = post_data['selftext']
                        url = post_data['url']
                        
                        # Buscar solicitudes de APIs
                        api_keywords = ['looking for api', 'need api', 'api for', 'is there an api for', 
                                      'api wrapper', 'rest api', 'graphql api']
                        
                        if any(keyword in title.lower() or keyword in selftext.lower() 
                              for keyword in api_keywords):
                            
                            opportunity = {
                                'name': f"Reddit Demand: {title[:50]}",
                                'description': f"Demand from r/{subreddit}: {title}",
                                'source_url': url,
                                'viability_score': 7.0,
                                'demand_metric': 8.0,
                                'implementation_complexity': 4.0,
                                'category': 'reddit_demand',
                                'tags': f'demand,reddit,{subreddit}'
                            }
                            opportunities.append(opportunity)
                            
            except Exception as e:
                print(f"❌ Error searching Reddit r/{subreddit}: {e}")
                
        return opportunities
    
    def calculate_viability(self, description):
        """Calcula viabilidad basada en keywords"""
        score = 5.0  # Base score
        
        positive_keywords = ['easy', 'simple', 'documented', 'popular', 'free', 'open source']
        negative_keywords = ['complex', 'difficult', 'paid', 'enterprise', 'complicated']
        
        for keyword in positive_keywords:
            if keyword in description.lower():
                score += 0.5
                
        for keyword in negative_keywords:
            if keyword in description.lower():
                score -= 0.5
                
        return min(max(score, 1.0), 10.0)
    
    def estimate_demand(self, title):
        """Estima demanda basada en el título"""
        demand_keywords = ['popular', 'trending', 'hot', 'most used', 'essential']
        score = 5.0
        
        for keyword in demand_keywords:
            if keyword in title.lower():
                score += 1.0
                
        return min(max(score, 1.0), 10.0)
    
    def save_opportunities(self, opportunities):
        """Guarda oportunidades en la base de datos"""
        db = SessionLocal()
        try:
            for opp_data in opportunities:
                opportunity = ApiOpportunity(**opp_data)
                db.add(opportunity)
            
            db.commit()
            print(f"✅ Guardadas {len(opportunities)} oportunidades en la base de datos")
        except Exception as e:
            db.rollback()
            print(f"❌ Error guardando oportunidades: {e}")
        finally:
            db.close()

def main():
    discovery = ApiDiscovery()
    
    print("🚀 Iniciando descubrimiento automático de APIs...")
    
    # Ejecutar diferentes métodos de descubrimiento
    github_opportunities = discovery.search_github_trending()
    reddit_opportunities = discovery.search_reddit_demand()
    
    all_opportunities = github_opportunities + reddit_opportunities
    
    if all_opportunities:
        discovery.save_opportunities(all_opportunities)
        print(f"🎯 Total oportunidades encontradas: {len(all_opportunities)}")
        
        # Mostrar resumen
        for opp in all_opportunities[:5]:
            print(f"📌 {opp['name']} - Score: {opp['viability_score']}/10")
    else:
        print("❌ No se encontraron oportunidades")

if __name__ == "__main__":
    main()
