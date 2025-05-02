from cloudscraper import CloudScraper
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Optional
from app.dtos.match_dto import PreviousMatchDTO, UpcomingMatchDTO
from app.config import Settings

class MatchService:

    def __init__(self, scraper: CloudScraper, settings: Settings):
        self.scraper = scraper
        self.base_url = settings.furia_hltv_url

    def _fetch_page_soup(self) -> BeautifulSoup:
        response = self.scraper.get(self.base_url)
        response.raise_for_status()
        return BeautifulSoup(response.content, "html.parser")

    def get_previous_matches(self) -> List[PreviousMatchDTO]:
        soup = self._fetch_page_soup()
        previous_matches = []
        results_header = soup.find("h2", string="Recent results for FURIA")
        if not results_header:
            return previous_matches

        recent_results_table = results_header.find_next_sibling("table", class_="match-table")
        if not recent_results_table:
            return previous_matches

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

        upcoming_results_table = upcoming_header.find_next_sibling("table", class_="match-table")
        if not upcoming_results_table:
            return upcoming_matches

        current_event = None
        for section in upcoming_results_table.find_all(["thead", "tbody"], recursive=False):
            if section.name == "thead":
                current_event = self._extract_event_name(section)
            elif section.name == "tbody":
                upcoming_matches.extend(self._extract_upcoming_matches(section, current_event))

        return upcoming_matches


    def _extract_event_name(self, section) -> str:
        event_link = section.find("a")
        return event_link.text.strip() if event_link else "Unknown Event"

    def _extract_previous_matches(self, section, event_name: str) -> List[PreviousMatchDTO]:
        matches = []
        for row in section.find_all("tr", class_="team-row"):
            try:
                date_cell = row.find("td", class_="date-cell")
                date_span = date_cell.find("span") if date_cell else None
                if not date_span: continue

                date_str = date_span.text.strip()

                try:
                    match_date = datetime.strptime(date_str, "%d/%m/%Y").date()
                except ValueError:
                    continue

                teams = row.find_all("a", class_="team-name")
                logos = row.find_all("img", class_="team-logo")
                score_cell = row.find("div", class_="score-cell")
                scores = score_cell.find_all("span", class_="score") if score_cell else []

                if len(teams) < 2 or len(logos) < 2 or len(scores) < 2:
                    continue


                team1_logo_src = logos[0].get("src", "")
                team2_logo_src = logos[1].get("src", "")


                try:
                    score1 = int(scores[0].text.strip())
                    score2 = int(scores[1].text.strip())
                except (ValueError, IndexError):
                    continue

                result_match = "WIN" if score1 > score2 else "LOST"

                match = PreviousMatchDTO(
                    team1_name=teams[0].text.strip(),
                    team2_name=teams[1].text.strip(),
                    team1_logo=team1_logo_src,
                    team2_logo=team2_logo_src,
                    team1_score=score1,
                    team2_score=score2,
                    match_date=match_date,
                    event_name=event_name,
                    result= result_match
                )
                matches.append(match)
            except Exception as e:
                print(f"Error parsing previous match row: {e}")
                continue
        return matches

    def _extract_upcoming_matches(self, section, event_name: Optional[str]) -> List[UpcomingMatchDTO]:
        matches = []
        for row in section.find_all("tr", class_="team-row"):
            try:
                date_cell = row.find("td", class_="date-cell")
                date_span = date_cell.find("span") if date_cell else None
                if not date_span: continue # Skip row if no date

                date_str = date_span.text.strip()
                 # Add error handling for date parsing
                try:
                    # Assuming upcoming matches only have date, not time on main page
                    match_date = datetime.strptime(date_str, "%d/%m/%Y").date()
                except ValueError:
                    continue # Skip row if date format is wrong

                teams = row.find_all("a", class_="team-name")
                logos = row.find_all("img", class_="team-logo")

                # Basic validation
                if len(teams) < 2 or len(logos) < 2:
                    continue # Skip malformed row

                # Add checks for logo src attribute
                team1_logo_src = logos[0].get("src", "")
                team2_logo_src = logos[1].get("src", "")

                match = UpcomingMatchDTO(
                    team1=teams[0].text.strip(),
                    team2=teams[1].text.strip(),
                    team1_logo=team1_logo_src,
                    team2_logo=team2_logo_src,
                    match_time=match_date, # Changed field name in DTO? Assuming it means date here.
                    event_name=event_name if event_name else "Unknown Event"
                )
                matches.append(match)
            except Exception as e:
                 # Log error for the specific row
                print(f"Error parsing upcoming match row: {e}")
                continue
        return matches