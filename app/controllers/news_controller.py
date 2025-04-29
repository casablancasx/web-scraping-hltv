

from fastapi import APIRouter

from app.dtos.news_dto import NewsDTO
from app.services.news_service import NewsService

router = APIRouter()
service = NewsService()


@router.get("/last_news", response_model=list[NewsDTO])
def get_furia_last_news():
    return service.get_furia_last_news()
