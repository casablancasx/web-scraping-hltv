
from typing import List
from fastapi import APIRouter

from app.dtos.championships_dto import ChampionshipsDTO
from app.services.championships_service import ChampionshipsService

router = APIRouter()
service = ChampionshipsService()

@router.get("/championships", response_model=List[ChampionshipsDTO])
def get_upcoming_championships():
    return service.scrape_upcoming_and_ongoing_championships()

