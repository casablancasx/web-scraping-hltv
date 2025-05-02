
from typing import List
from fastapi import APIRouter, Depends

from app.dtos.trophy_dto import TrophyDTO
from app.services.trophy_service import TrophyService
from app.dependencies import get_trophy_service 

router = APIRouter(prefix="/trophies", tags=["Trophies"]) 


@router.get("", response_model=List[TrophyDTO]) 
def get_trophy_info(service: TrophyService = Depends(get_trophy_service)): 
    return service.get_trophy_info()