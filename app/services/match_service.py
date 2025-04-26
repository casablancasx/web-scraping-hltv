import cloudscraper
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List
from app.dtos.match_dto import PreviousMatchDTO, UpcomingMatchDTO

class MatchService:
    BASE_URL = "https://www.hltv.org/team/8297/furia"

    def __init__(self):
        self.scraper = cloudscraper.create_scraper()

    def get_previous_matches(self) -> List[PreviousMatchDTO]:
        soup = self._fetch_page_soup()
        recent_results_table = soup.find("h2", string="Recent results for FURIA").find_next("table")

        previous_matches = []
        current_event = ""

        for section in recent_results_table.find_all(["thead", "tbody"], recursive=False):
            if section.name == "thead":
                current_event = self._extract_event_name(section)
            elif section.name == "tbody":
                previous_matches.extend(self._extract_previous_matches(section, current_event))

        return previous_matches

    def get_upcoming_matches(self) -> List[UpcomingMatchDTO]:
        soup = self._fetch_page_soup()

        upcoming_matches = []
        upcoming_header = soup.find("h2", string="Upcoming matches for FURIA")
        if not upcoming_header:
            return upcoming_matches

        current = upcoming_header
        current_event = None

        while True:
            current = current.find_next_sibling()
            if not current or current.name == "h2":
                break

            if current.name == "table" and "match-table" in current.get("class", []):
                for section in current.find_all(["thead", "tbody"], recursive=False):
                    if section.name == "thead":
                        current_event = self._extract_event_name(section)
                    elif section.name == "tbody":
                        upcoming_matches.extend(self._extract_upcoming_matches(section, current_event))

        return upcoming_matches

    def _fetch_page_soup(self) -> BeautifulSoup:
        response = self.scraper.get(self.BASE_URL)
        response.raise_for_status()
        return BeautifulSoup(response.content, "html.parser")

    def _extract_event_name(self, section) -> str:
        event_link = section.find("a")
        return event_link.text.strip() if event_link else ""

    def _extract_previous_matches(self, section, event_name: str) -> List[PreviousMatchDTO]:
        matches = []
        for row in section.find_all("tr", class_="team-row"):
            date_str = row.find("td", class_="date-cell").find("span").text.strip()
            match_date = datetime.strptime(date_str, "%d/%m/%Y")

            teams = row.find_all("a", class_="team-name")
            logos = row.find_all("img", class_="team-logo")
            scores = row.find("div", class_="score-cell").find_all("span", class_="score")

            match = PreviousMatchDTO(
                team1=teams[0].text.strip(),
                team2=teams[1].text.strip(),
                team1_logo=logos[0]["src"],
                team2_logo=logos[1]["src"],
                score1=int(scores[0].text.strip()),
                score2=int(scores[1].text.strip()),
                date=match_date,
                event_name=event_name
            )
            matches.append(match)
        return matches

    def _extract_upcoming_matches(self, section, event_name: str) -> List[UpcomingMatchDTO]:
        matches = []
        for row in section.find_all("tr", class_="team-row"):
            date_span = row.find("td", class_="date-cell").find("span")
            if not date_span:
                continue

            date_str = date_span.text.strip()
            match_time = datetime.strptime(date_str, "%d/%m/%Y")

            teams = row.find_all("a", class_="team-name")
            logos = row.find_all("img", class_="team-logo")

            if len(teams) < 2 or len(logos) < 2:
                continue

            match = UpcomingMatchDTO(
                team1=teams[0].text.strip(),
                team2=teams[1].text.strip(),
                team1_logo=logos[0]["src"],
                team2_logo=logos[1]["src"],
                match_time=match_time,
                event_name=event_name
            )
            matches.append(match)
        return matches
