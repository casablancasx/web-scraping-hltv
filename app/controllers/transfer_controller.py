from typing import List

from fastapi import APIRouter
from app.services.transfer_service import TransferService
from app.dtos.transfer_dto import TransferDTO

router = APIRouter()
service =  TransferService()


@router.get("/transfer", response_model=List[TransferDTO])
def get_info_team():
    return service.get_transfer_info()

