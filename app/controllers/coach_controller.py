from fastapi import APIRouter, Depends, HTTPException 
from app.dtos.coach_dto import CoachInfoDTO
from app.services.coach_service import CoachService
from app.dependencies import get_coach_service 

router = APIRouter(prefix="/coach", tags=["Coach"])

@router.get("", response_model=CoachInfoDTO) 
def get_coach_info(service: CoachService = Depends(get_coach_service)): 
    try:
        return service.get_detailed_coach()
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
   
        raise HTTPException(status_code=500, detail="Internal server error while fetching coach details.")
