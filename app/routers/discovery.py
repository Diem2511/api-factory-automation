from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from ..db import get_db
from ..services.discovery import discover_github, persist_discoveries
from ..schemas import OpportunityOut
router = APIRouter()
@router.get("/discover", response_model=dict)
def discover(limit: int = Query(5, ge=1, le=50), db: Session = Depends(get_db)):
    items = discover_github(limit=limit)
    saved = persist_discoveries(db, items)
    out = [OpportunityOut.model_validate(s) for s in saved]
    return {"items": out}
