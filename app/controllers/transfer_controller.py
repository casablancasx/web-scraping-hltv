
from typing import List
from fastapi import APIRouter, Depends 
from app.services.transfer_service import TransferService
from app.dtos.transfer_dto import TransferDTO
from app.dependencies import get_transfer_service 

router = APIRouter(prefix="/transfers", tags=["Transfers"]) 


@router.get("", response_model=List[TransferDTO]) 
def get_transfer_info(service: TransferService = Depends(get_transfer_service)): 
    return service.get_transfer_info()