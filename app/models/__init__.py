from typing import Optional
from app.db import Base, engine as default_engine

def create_tables(engine: Optional[object] = None) -> None:
    """
    Crea todas las tablas registradas en Base.metadata.
    Si no pasas engine, usa el engine por defecto.
    """
    eng = engine or default_engine
    Base.metadata.create_all(bind=eng)
