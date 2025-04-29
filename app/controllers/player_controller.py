from typing import List

from fastapi import APIRouter

from app.dtos.player_dto import DetailedPlayerDTO
from app.services.player_service import PlayerService

router = APIRouter()
service =  PlayerService()


@router.get("/player", response_model=List[DetailedPlayerDTO])
def get_info_team():
    return service.get_detailed_player()

