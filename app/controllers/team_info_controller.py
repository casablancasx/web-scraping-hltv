from fastapi import APIRouter, Depends, HTTPException
from app.services.info_team_service import InfoTeamService
from app.dtos.team_info_dto import InfoTeamDTO
from app.dependencies import get_info_team_service

router = APIRouter(prefix="/team", tags=["Team Info"])

@router.get("", response_model=InfoTeamDTO)
def get_info_team(service: InfoTeamService = Depends(get_info_team_service)):
    try:
        return service.get_team_info()
    except Exception as e:
        # Log the error e
        # Basic error handling
        raise HTTPException(status_code=500, detail="Failed to retrieve team information.")