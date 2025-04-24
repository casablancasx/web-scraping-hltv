from fastapi import APIRouter
from app.services.match_service import MatchService
from app.dtos.match_dto import PreviousMatchDTO, UpcomingMatchDTO
from typing import List

router = APIRouter()
service = MatchService()

@router.get("/matches/previous", response_model=List[PreviousMatchDTO])
def get_previous_matches():
    return service.get_previous_matches()

@router.get("/matches/upcoming", response_model=List[UpcomingMatchDTO])
def get_upcoming_matches():
    return service.get_upcoming_matches()
