
from typing import List
from fastapi import APIRouter

from app.dtos.trophy_dto import TrophyDTO
from app.services.trophy_service import TrophyService


router = APIRouter()
service = TrophyService()

@router.get("/trophy", response_model=List[TrophyDTO])
def get_trophy_info():
    return service.get_trophy_info()