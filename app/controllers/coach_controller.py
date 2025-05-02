
from fastapi import APIRouter

from app.dtos.coach_dto import CoachInfoDTO
from app.services.coach_service import CoachService

router = APIRouter()
service = CoachService()


@router.get("/coach", response_model=CoachInfoDTO)
def get_info_team():
    return service.get_detailed_coach()

