from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# Usar la DATABASE_URL de Railway o una local para desarrollo
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Definición de tu modelo de API
class APIEndpoint(Base):
    __tablename__ = "api_endpoints"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    url = Column(String(500), nullable=False)
    method = Column(String(10), nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)

# Función para crear las tablas
def create_tables():
    print("Attempting to create database tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully (if they didn't exist).")

# Función para obtener una sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
