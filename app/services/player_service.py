from typing import List
from bs4 import BeautifulSoup
import os
import cloudscraper

from app.dtos.player_dto import DetailedPlayerDTO


class PlayerService:
    BASE_URL = os.getenv("FURIA_HLTV_URL", "https://www.hltv.org/team/8297/furia")

    def __init__(self):
        self.scraper = cloudscraper.create_scraper()

    def _fetch_page_soup(self) -> BeautifulSoup:
        response = self.scraper.get(self.BASE_URL)
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
            maps_text = cells[3].text.strip()
            if maps_text.isdigit():
                maps_played = int(maps_text)
            else:
                maps_played = 0

        rating = 0.0
        if len(cells) > 4:
            rating_text = cells[4].text.strip().split()[0]
            try:
                rating = float(rating_text)
            except ValueError:
                rating = 0.0

        return DetailedPlayerDTO(
            player_img=player_img_tag['src'] if player_img_tag else "",
            nickname=nickname_tag.text.strip() if nickname_tag else "",
            nationality=nationality_tag['title'] if nationality_tag else "",
            status=status_tag.text.strip() if status_tag else "",
            rating=rating,
            maps_played=maps_played
        )
