from functools import lru_cache
import cloudscraper
from cloudscraper import CloudScraper
from fastapi import Depends

from app.config import Settings, settings as global_settings

@lru_cache()
def get_settings() -> Settings:
    return global_settings

@lru_cache()
def get_scraper() -> CloudScraper:
    try:
        scraper = cloudscraper.create_scraper()
        return scraper
    except Exception as e:
        print(f"Error creating CloudScraper instance: {e}")
        raise RuntimeError("Could not initialize the web scraper.") from e


from app.services.transfer_service import TransferService
from app.services.news_service import NewsService
from app.services.match_service import MatchService
from app.services.info_team_service import InfoTeamService
from app.services.championships_service import ChampionshipsService




def get_transfer_service(
    scraper: CloudScraper = Depends(get_scraper),
    settings: Settings = Depends(get_settings)
) -> TransferService:
    return TransferService(scraper=scraper, settings=settings)


def get_news_service(
    scraper: CloudScraper = Depends(get_scraper),
    settings: Settings = Depends(get_settings)
) -> NewsService:
    return NewsService(scraper=scraper, settings=settings)

def get_match_service(
    scraper: CloudScraper = Depends(get_scraper),
    settings: Settings = Depends(get_settings)
) -> MatchService:
    return MatchService(scraper=scraper, settings=settings)

def get_info_team_service(
    scraper: CloudScraper = Depends(get_scraper),
    settings: Settings = Depends(get_settings)
) -> InfoTeamService:
    return InfoTeamService(scraper=scraper, settings=settings)


def get_championships_service(
    scraper: CloudScraper = Depends(get_scraper),
    settings: Settings = Depends(get_settings)
) -> ChampionshipsService:
    return ChampionshipsService(scraper=scraper, settings=settings)