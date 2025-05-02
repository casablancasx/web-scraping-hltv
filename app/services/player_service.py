
from typing import List
from bs4 import BeautifulSoup
from cloudscraper import CloudScraper

from app.dtos.player_dto import DetailedPlayerDTO
from app.config import Settings


class PlayerService:

    def __init__(self, scraper: CloudScraper, settings: Settings):
        self.scraper = scraper
        self.base_url = settings.furia_hltv_url

    def _fetch_page_soup(self) -> BeautifulSoup:
        response = self.scraper.get(self.base_url)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")

    def get_detailed_player(self) -> List[DetailedPlayerDTO]:
        soup = self._fetch_page_soup()
        player_rows = soup.select('.players-table tbody tr')

        players = []
        for row in player_rows:
            player = self._parse_player_row(row)
            if player:
                players.append(player)

        return players

    def _parse_player_row(self, row) -> DetailedPlayerDTO:
        player_img_tag = row.select_one('.playersBox-img-wrapper img')
        nickname_tag = row.select_one('.playersBox-playernick div.text-ellipsis')
        nationality_tag = row.select_one('.playersBox-playernick img.flag')
        status_tag = row.select_one('.status-cell .player-status')

        cells = row.select('td')

        maps_played = 0
        if len(cells) > 3:
            maps_cell = cells[3]
            if maps_cell:
                maps_text = maps_cell.text.strip()
                if maps_text.isdigit():
                    maps_played = int(maps_text)

        rating = 0.0
        if len(cells) > 4:
            rating_cell = cells[4]
            if rating_cell:
                rating_text = rating_cell.text.strip().split()[0]
                try:
                    rating = float(rating_text)
                except ValueError:
                    rating = 0.0

        return DetailedPlayerDTO(
            player_img=player_img_tag['src'] if player_img_tag and player_img_tag.has_attr('src') else "",
            nickname=nickname_tag.text.strip() if nickname_tag else "N/A",
            nationality=nationality_tag['title'] if nationality_tag and nationality_tag.has_attr('title') else "N/A",
            status=status_tag.text.strip() if status_tag else "N/A",
            rating=rating,
            maps_played=maps_played
        )