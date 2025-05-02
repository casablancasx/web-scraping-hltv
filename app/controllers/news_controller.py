
from typing import List
from fastapi import APIRouter, Depends, HTTPException

from app.dtos.news_dto import NewsDTO
from app.services.news_service import NewsService
from app.dependencies import get_news_service


router = APIRouter(prefix="/news", tags=["News"])




@router.get("/latest", response_model=List[NewsDTO])
def get_furia_last_news(service: NewsService = Depends(get_news_service)):
    try:
        return service.get_furia_last_news()
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to retrieve latest news.")