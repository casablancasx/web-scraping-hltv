
from bs4 import BeautifulSoup
import cloudscraper
from cloudscraper import CloudScraper

from app.dtos.coach_dto import CoachInfoDTO
from app.config import Settings


class CoachService:
    def __init__(self, scraper: CloudScraper, settings: Settings):
        self.scraper = scraper
        self.base_url = settings.furia_hltv_url

    def _fetch_page_soup(self) -> BeautifulSoup:
        response = self.scraper.get(self.base_url)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")

    def get_detailed_coach(self) -> CoachInfoDTO:
        soup = self._fetch_page_soup()

        table = soup.find("table", class_="table-container coach-table")
        if not table:
            raise ValueError("Coach table not found on the page.")

        tbody = table.find("tbody")
        if not tbody:
            raise ValueError("Coach table body not found.")

        row = tbody.find("tr")
        if not row:
            raise ValueError("No coach data row found.")

        coach_img_tag = row.find("div", class_="playersBox-img-wrapper").find("img")
        coach_img = coach_img_tag["src"] if coach_img_tag else ""

        nickname_tag = row.find("div", class_="players-cell playersBox-playernick text-ellipsis")
        nickname = nickname_tag.text.strip() if nickname_tag else "N/A"

        cells = row.find_all("div", class_="players-cell center-cell opacity-cell")
        maps_played = 0
        trophies_won = 0
        if len(cells) > 2:
            try:
                maps_played = int(cells[1].text.strip())
            except (ValueError, IndexError):
                maps_played = 0 # Default or log error
            try:
                trophies_won = int(cells[2].text.strip())
            except (ValueError, IndexError):
                trophies_won = 0 # Default or log error

        winrate_tag = row.find("div", class_="players-cell rating-cell")
        winrate = winrate_tag.text.strip() if winrate_tag else "N/A"

        return CoachInfoDTO(
            coach_img=coach_img,
            nickname=nickname,
            maps_played=maps_played,
            trophies_won=trophies_won,
            winrate=winrate 
        )