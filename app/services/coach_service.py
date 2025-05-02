from bs4 import BeautifulSoup
import os
import cloudscraper

from app.dtos.coach_dto import CoachInfoDTO


class CoachService:
    BASE_URL = os.getenv("FURIA_HLTV_URL", "https://www.hltv.org/team/8297/furia")

    def __init__(self):
        self.scraper = cloudscraper.create_scraper()

    def _fetch_page_soup(self) -> BeautifulSoup:
        response = self.scraper.get(self.BASE_URL)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")

    def get_detailed_coach(self) -> CoachInfoDTO:
        soup = self._fetch_page_soup()

        # Localiza a tabela de coaches
        table = soup.find("table", class_="table-container coach-table")
        row = table.find("tbody").find("tr")

        # Extrai os dados da linha
        coach_img = row.find("div", class_="playersBox-img-wrapper").find("img")["src"]
        nickname = row.find("div", class_="players-cell playersBox-playernick text-ellipsis").text.strip()
        maps_played = int(row.find_all("div", class_="players-cell center-cell opacity-cell")[1].text.strip())
        trophies_won = int(row.find_all("div", class_="players-cell center-cell opacity-cell")[2].text.strip())
        winrate = row.find("div", class_="players-cell rating-cell").text.strip()

        # Retorna os dados no formato CoachInfoDTO
        return CoachInfoDTO(
            coach_img=coach_img,
            nickname=nickname,
            maps_played=maps_played,
            trophies_won=trophies_won,
            winrante=winrate
        )



