from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Usar la DATABASE_URL de Railway o local
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
    parameters = Column(Text)
    response_schema = Column(Text)
    is_active = Column(Boolean, default=True)

def create_tables():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
