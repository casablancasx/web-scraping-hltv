import logging
from fastapi import APIRouter, Depends, HTTPException
from app.services.info_team_service import InfoTeamService
from app.dtos.team_info_dto import InfoTeamDTO
from app.dependencies import get_info_team_service

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


router = APIRouter(prefix="/team", tags=["Team Info"])

@router.get("", response_model=InfoTeamDTO)
def get_info_team(service: InfoTeamService = Depends(get_info_team_service)):
    try:
        return service.get_team_info()
    except Exception as e:
        log.error(f"Error retrieving team info: {e}", exc_info=True) # Log the exception details
        raise HTTPException(status_code=500, detail="Failed to retrieve team information.")
