from typing import List, Optional
from bs4 import BeautifulSoup
from cloudscraper import CloudScraper
from datetime import datetime
from app.dtos.transfer_dto import TransferDTO
from app.config import Settings

class TransferService:
    def __init__(self, scraper: CloudScraper, settings: Settings):
        self.scraper = scraper
        self.base_url = settings.furia_hltv_url

    def _fetch_page_soup(self) -> BeautifulSoup:
        response = self.scraper.get(self.base_url)
        response.raise_for_status()
        return BeautifulSoup(response.content, "html.parser")

    def get_transfer_info(self) -> List[TransferDTO]:
        soup = self._fetch_page_soup()
        transfer_rows = soup.select('.transfer-row')

        transfers = []
        for row in transfer_rows:
            transfer = self._parse_transfer_row(row)
            if transfer:
                transfers.append(transfer)

        return transfers

    def _parse_transfer_row(self, row) -> Optional[TransferDTO]:
        nickname = self._extract_nickname(row)
        player_img = self._extract_player_img(row)
        action, text = self._extract_action(row)
        from_team, to_team, from_team_img, to_team_img = self._extract_teams(row, text)
        role = self._extract_role(row)
        transfer_date = self._extract_date(row)

        if nickname and action and transfer_date:
            return TransferDTO(
                player_img=player_img if player_img else "", # Ensure non-optional
                nickname=nickname,
                role=role,
                action=action,
                from_team=from_team,
                from_team_img=from_team_img,
                to_team=to_team,
                to_team_img=to_team_img,
                date=transfer_date
            )
        return None

    def _extract_nickname(self, row) -> Optional[str]:
        tag = row.select_one('.transfer-movement a b')
        return tag.text.strip() if tag else None

    def _extract_player_img(self, row) -> Optional[str]:
        img_tag = row.select_one('.transfer-player-image')
        return img_tag['src'] if img_tag else None

    def _extract_action(self, row) -> tuple[Optional[str], str]:
        movement_tag = row.select_one('.transfer-movement')
        if not movement_tag:
            return None, ""

        text = movement_tag.text.lower()
        if "transfer" in text:
            return "transfer", text
        if "bench" in text:
            return "bench", text
        if "join" in text:
            return "join", text
        if "part ways" in text or "parts ways" in text:
            return "part ways", text
        return None, text

    def _extract_teams(self, row, text: str) -> tuple[Optional[str], Optional[str], Optional[str], Optional[str]]:
        teams = row.select('.transfer-team-container')
        from_team = from_team_img = None
        to_team = to_team_img = None

        if len(teams) >= 1:
            from_team_tag = teams[0].select_one('.transfer-team-logo')
            if from_team_tag and from_team_tag.get('title') and from_team_tag['title'] != "?":
                from_team = from_team_tag['title']
                from_team_img = from_team_tag['src']

        if len(teams) >= 2:
            to_team_tag = teams[1].select_one('.transfer-team-logo')
            if to_team_tag and to_team_tag.get('title') and to_team_tag['title'] != "?":
                to_team = to_team_tag['title']
                to_team_img = to_team_tag['src']

        return from_team, to_team, from_team_img, to_team_img

    def _extract_role(self, row) -> str:
        statuses = row.select('.transfer-team-status')
        for status_tag in statuses:
            status_text = status_tag.text.strip().lower()
            if status_text == "coach":
                return "Coach"
        return "Player"

    def _extract_date(self, row) -> Optional[datetime.date]:
        date_tag = row.select_one('.transfer-date')
        if date_tag and date_tag.get('data-unix'):
            try:
                timestamp = int(date_tag['data-unix']) / 1000
                return datetime.utcfromtimestamp(timestamp).date()
            except (ValueError, TypeError):
                return None
        return None