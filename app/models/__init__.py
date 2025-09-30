from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
import os

# Configuración de la base de datos
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/api_factory")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class APIEndpoint(Base):
    __tablename__ = "api_endpoints"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True)
    url = Column(String(500))
    method = Column(String(10))
    description = Column(Text)
    parameters = Column(JSON)  # Cambiado a JSON
    response_schema = Column(JSON)  # Cambiado a JSON
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class APIService(Base):
    __tablename__ = "api_services"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True)
    base_url = Column(String(500))
    description = Column(Text)
    authentication_type = Column(String(50))  # 'api_key', 'oauth', 'none'
    auth_config = Column(JSON)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class WrapperConfig(Base):
    __tablename__ = "wrapper_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True)
    target_api_id = Column(Integer)
    wrapper_type = Column(String(50))  # 'rest', 'graphql', 'websocket'
    config = Column(JSON)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

def create_tables():
    Base.metadata.create_all(bind=engine)
    print("✅ Tablas de base de datos creadas exitosamente")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
