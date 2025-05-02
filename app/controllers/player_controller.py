from typing import List
from fastapi import APIRouter, Depends, HTTPException

from app.dtos.player_dto import DetailedPlayerDTO
from app.services.player_service import PlayerService
from app.dependencies import get_player_service


router = APIRouter(prefix="/players", tags=["Players"])

@router.get("/detailed", response_model=List[DetailedPlayerDTO])
def get_detailed_players(service: PlayerService = Depends(get_player_service)):
    try:
        return service.get_detailed_player()
    except Exception as e:
        # Log the error e
        raise HTTPException(status_code=500, detail="Failed to retrieve detailed player information.")

# Note: You might want separate endpoints for active vs detailed players later