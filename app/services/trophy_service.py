from bs4 import BeautifulSoup
from cloudscraper import CloudScraper

from app.dtos.trophy_dto import TrophyDTO
from app.config import Settings


class TrophyService:
    def __init__(self, scraper: CloudScraper, settings: Settings):
        self.scraper = scraper
        self.base_url = settings.furia_hltv_url

    def _fetch_page_soup(self) -> BeautifulSoup:
        response = self.scraper.get(self.base_url)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'html.parser')

    def get_trophy_info(self) -> list[TrophyDTO]:
        soup = self._fetch_page_soup()
        trophy_rows = soup.select('.trophyRow a.trophy')

        trophies = []
        for trophy in trophy_rows:
            event_name = trophy.find('span', class_='trophyDescription')['title']
            img_tag = trophy.find('img')

            trophy_img = img_tag['src']
            if trophy_img.startswith('/'):
                trophy_img = f"https://www.hltv.org{trophy_img}"

            hltv_event_link = f"https://www.hltv.org{trophy['href']}"

            trophy_dto = TrophyDTO(
                event_name=event_name,
                trophy_img=trophy_img,
                hltv_event_link=hltv_event_link
            )
            trophies.append(trophy_dto)

        return trophies