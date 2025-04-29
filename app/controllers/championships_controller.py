
from typing import List
from fastapi import APIRouter

from app.dtos.championships_dto import UpComingChampionshipsDto, PreviousChampionshipsDto
from app.services.championships_service import ChampionshipsService

router = APIRouter()
service = ChampionshipsService()

@router.get("/championships/upcoming", response_model=List[UpComingChampionshipsDto])
def get_upcoming_championships():
    return service.scrape_upcoming_championships()

