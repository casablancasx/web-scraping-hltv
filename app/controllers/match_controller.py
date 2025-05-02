from fastapi import APIRouter, Depends, HTTPException
from app.services.match_service import MatchService
from app.dtos.match_dto import PreviousMatchDTO, UpcomingMatchDTO
from typing import List
from app.dependencies import get_match_service


router = APIRouter(prefix="/matches", tags=["Matches"])



@router.get("/previous", response_model=List[PreviousMatchDTO])
def get_previous_matches(service: MatchService = Depends(get_match_service)):
    try:
        return service.get_previous_matches()
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to retrieve previous matches.")


@router.get("/upcoming", response_model=List[UpcomingMatchDTO])
def get_upcoming_matches(service: MatchService = Depends(get_match_service)):
    try:
        return service.get_upcoming_matches()
    except Exception as e:
        # Log the error e
        raise HTTPException(status_code=500, detail="Failed to retrieve upcoming matches.")