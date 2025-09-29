from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text
from sqlalchemy.sql import func
from app.database import Base

class ApiOpportunity(Base):
    __tablename__ = "api_opportunities"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    source_url = Column(String)
    viability_score = Column(Float)
    demand_metric = Column(Float)
    implementation_complexity = Column(Float)
    estimated_revenue = Column(Float)
    category = Column(String)
    tags = Column(String)
    is_processed = Column(Boolean, default=False)
    is_deployed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
