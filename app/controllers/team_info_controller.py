from fastapi import APIRouter
from app.services.info_team_service import InfoTeamService
from app.dtos.team_info_dto import InfoTeamDTO

router = APIRouter()
service =  InfoTeamService()


@router.get("/team", response_model=InfoTeamDTO)
def get_info_team():
    return service.get_team_info()

