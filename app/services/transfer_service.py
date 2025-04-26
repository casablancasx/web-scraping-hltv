from typing import List, Optional
from bs4 import BeautifulSoup
import cloudscraper
from datetime import datetime
from app.dtos.transfer_dto import TransferDTO

class TransferService:
    BASE_URL = "https://www.hltv.org/team/8297/furia"

    def __init__(self):
        self.scraper = cloudscraper.create_scraper()

    def get_transfer_info(self) -> List[TransferDTO]:
        soup = self._fetch_page_soup()
        transfer_rows = soup.select('.transfer-row')

        transfers = []
        for row in transfer_rows:
            transfer = self._parse_transfer_row(row)
            if transfer:
                transfers.append(transfer)

        return transfers

    def _fetch_page_soup(self) -> BeautifulSoup:
        response = self.scraper.get(self.BASE_URL)
        response.raise_for_status()
        return BeautifulSoup(response.content, "html.parser")

    def _parse_transfer_row(self, row) -> Optional[TransferDTO]:
        nickname = self._extract_nickname(row)
        action, text = self._extract_action(row)
        from_team, to_team = self._extract_teams(row, text)
        role = self._extract_role(row)
        date = self._extract_date(row)

        if nickname and action and date:
            return TransferDTO(
                nickname=nickname,
                role=role,
                action=action,
                from_team=from_team,
                to_team=to_team,
                date=date
            )
        return None

    def _extract_nickname(self, row) -> Optional[str]:
        tag = row.select_one('.transfer-movement a b')
        return tag.text.strip() if tag else None

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

    def _extract_teams(self, row, text: str) -> tuple[Optional[str], Optional[str]]:
        links = row.select('.transfer-movement a')

        from_team = None
        if len(links) >= 2:
            from_team = links[1].text.strip()
        elif "no team" in text:
            from_team = "No team"

        to_team = None
        if len(links) >= 3:
            to_team = links[2].text.strip()
        elif "joins" in text or "is benched" in text or "parts ways" in text:
            to_team = "FURIA"

        return from_team, to_team

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
            timestamp = int(date_tag['data-unix']) / 1000
            return datetime.utcfromtimestamp(timestamp).date()
        return None
