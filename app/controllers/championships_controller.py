from typing import List
from fastapi import APIRouter, Depends, HTTPException # Import Depends, HTTPException
from app.dtos.championships_dto import ChampionshipsDTO
from app.services.championships_service import ChampionshipsService
from app.dependencies import get_championships_service


router = APIRouter(prefix="/championships", tags=["Championships"])

@router.get("/active", response_model=List[ChampionshipsDTO])
def get_active_championships(service: ChampionshipsService = Depends(get_championships_service)):
    try:
        return service.scrape_upcoming_and_ongoing_championships()
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to retrieve active championships.")