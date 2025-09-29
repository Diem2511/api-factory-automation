from fastapi import APIRouter, Query
from ..services.open_meteo import get_weather

router = APIRouter(prefix="/wrappers")

@router.get("/weather")
async def weather(lat: float = Query(...), lon: float = Query(...)):
    return await get_weather(lat, lon)
