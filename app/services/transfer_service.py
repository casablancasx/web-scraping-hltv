from typing import List
from bs4 import BeautifulSoup
import cloudscraper
from datetime import datetime
from app.dtos.transfer_dto import TransferDTO  # Seu DTO

class TransferService:
    def __init__(self):
        self.url = "https://www.hltv.org/team/8297/furia"
        self.scraper = cloudscraper.create_scraper()

    def get_transfer_info(self) -> List[TransferDTO]:
        response = self.scraper.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")

        transfer_list = []
        transfer_rows = soup.select('.transfer-row')

        for row in transfer_rows:
            nickname_tag = row.select_one('.transfer-movement a b')
            nickname = nickname_tag.text.strip() if nickname_tag else None

            movement_text = row.select_one('.transfer-movement')
            action = None
            if movement_text:
                text = movement_text.text.lower()
                if "transfer" in text:
                    action = "transfer"
                elif "bench" in text:
                    action = "bench"
                elif "join" in text:
                    action = "join"
                elif "part ways" in text or "parts ways" in text:
                    action = "part ways"

            from_team = None
            movement_links = row.select('.transfer-movement a')
            if len(movement_links) >= 2:
                from_team = movement_links[1].text.strip()
            elif "no team" in text:
                from_team = "No team"

            to_team = None
            if len(movement_links) >= 3:
                to_team = movement_links[2].text.strip()
            elif "joins" in text or "is benched" in text or "parts ways" in text:
                to_team = "FURIA"  # Default para FURIA porque estamos pegando da página deles

            role = "Player"
            team_statuses = row.select('.transfer-team-status')
            if team_statuses:
                for status_tag in team_statuses:
                    status_text = status_tag.text.strip().lower()
                    if status_text == "coach":
                        role = "Coach"
                        break

            date_tag = row.select_one('.transfer-date')
            date = None
            if date_tag and date_tag.get('data-unix'):
                unix_timestamp = int(date_tag['data-unix']) / 1000
                date = datetime.utcfromtimestamp(unix_timestamp).date()

            if nickname and action and date:
                transfer = TransferDTO(
                    nickname=nickname,
                    role=role,
                    action=action,
                    from_team=from_team,
                    to_team=to_team,
                    date=date
                )
                transfer_list.append(transfer)

        return transfer_list
