from cloudscraper import CloudScraper
from bs4 import BeautifulSoup, Tag
from datetime import datetime
from typing import List, Optional
from app.dtos.match_dto import PreviousMatchDTO, UpcomingMatchDTO
from app.config import Settings
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class MatchService:

    def __init__(self, scraper: CloudScraper, settings: Settings):
        self.scraper = scraper
        self.base_url = settings.furia_hltv_url
        self.furia_team_id = "8297"

    def _fetch_page_soup(self) -> Optional[BeautifulSoup]:
        try:
            response = self.scraper.get(self.base_url)
            response.raise_for_status()
            return BeautifulSoup(response.content, "html.parser")
        except Exception as e:
            logging.error(f"Error fetching page {self.base_url}: {e}")
            return None

    def _safe_get_text(self, tag: Optional[Tag], default: str = "") -> str:
        return tag.text.strip() if tag else default

    def _safe_get_attr(self, tag: Optional[Tag], attr: str, default: str = "") -> str:
        return tag.get(attr, default) if tag else default

    def _parse_date(self, date_str: str) -> Optional[datetime.date]:
        try:
            return datetime.strptime(date_str, "%d/%m/%Y").date()
        except ValueError:
            logging.warning(f"Could not parse date string: {date_str}")
            return None

    def _extract_event_name(self, thead_section: Tag) -> str:
        event_link = thead_section.select_one("tr.event-header-cell th a")
        return self._safe_get_text(event_link, "Unknown Event")

    def _extract_previous_matches(self, tbody_section: Tag, event_name: str) -> List[PreviousMatchDTO]:
        matches = []
        for row in tbody_section.find_all("tr", class_="team-row"):
            try:
                date_cell = row.find("td", class_="date-cell")
                date_span = date_cell.find("span") if date_cell else None
                date_str = self._safe_get_text(date_span)
                match_date = self._parse_date(date_str)
                if not match_date:
                    continue

                team_cells = row.select(".team-center-cell .team-flex")
                score_cell = row.find("div", class_="score-cell")
                scores = score_cell.find_all("span", class_="score") if score_cell else []

                if len(team_cells) < 2 or len(scores) < 2:
                    logging.warning(f"Skipping previous match row due to missing team/score data: {row}")
                    continue

                team1_div = team_cells[0]
                team2_div = team_cells[1]

                team1_name = self._safe_get_text(team1_div.find("a", class_="team-name"))
                team2_name = self._safe_get_text(team2_div.find("a", class_="team-name"))

                team1_logo_tag = team1_div.select_one(".team-logo-container img.team-logo")
                team2_logo_tag = team2_div.select_one(".team-logo-container img.team-logo")
                team1_logo = self._safe_get_attr(team1_logo_tag, "src")
                team2_logo = self._safe_get_attr(team2_logo_tag, "src")

                try:
                    score1 = int(self._safe_get_text(scores[0]))
                    score2 = int(self._safe_get_text(scores[1]))
                except (ValueError, IndexError):
                    logging.warning(f"Could not parse scores for previous match: {row}")
                    continue


                result_match = "LOST" if "lost" in team1_div.get("class", []) else "WIN"

                match = PreviousMatchDTO(
                    team1_name=team1_name,
                    team2_name=team2_name,
                    team1_logo=team1_logo,
                    team2_logo=team2_logo,
                    team1_score=score1,
                    team2_score=score2,
                    match_date=match_date,
                    event_name=event_name,
                    result=result_match
                )
                matches.append(match)
            except Exception as e:
                logging.error(f"Error parsing previous match row: {e} | Row: {row}", exc_info=True)
                continue
        return matches

    def _extract_upcoming_matches(self, tbody_section: Tag, event_name: Optional[str]) -> List[UpcomingMatchDTO]:
        matches = []
        for row in tbody_section.find_all("tr", class_="team-row"):
            try:
                date_cell = row.find("td", class_="date-cell")
                date_span = date_cell.find("span") if date_cell else None
                date_str = self._safe_get_text(date_span)
                match_date = self._parse_date(date_str)
                if not match_date:
                    continue

                team_cells = row.select(".team-center-cell .team-flex")
                if len(team_cells) < 2:
                    logging.warning(f"Skipping upcoming match row due to missing team data: {row}")
                    continue

                team1_div = team_cells[0]
                team2_div = team_cells[1]

                team1_name = self._safe_get_text(team1_div.find("a", class_="team-name"))
                team2_name = self._safe_get_text(team2_div.find("a", class_="team-name"))

                team1_logo_tag = team1_div.select_one(".team-logo-container img.team-logo")
                team2_logo_tag = team2_div.select_one(".team-logo-container img.team-logo")
                team1_logo = self._safe_get_attr(team1_logo_tag, "src")
                team2_logo = self._safe_get_attr(team2_logo_tag, "src")

                match = UpcomingMatchDTO(
                    team1=team1_name,
                    team2=team2_name,
                    team1_logo=team1_logo,
                    team2_logo=team2_logo,
                    match_time=match_date,
                    event_name=event_name if event_name else "Unknown Event"
                )
                matches.append(match)
            except Exception as e:
                logging.error(f"Error parsing upcoming match row: {e} | Row: {row}", exc_info=True)
                continue
        return matches

    def get_previous_matches(self) -> List[PreviousMatchDTO]:
        soup = self._fetch_page_soup()
        if not soup:
            return []

        previous_matches = []
        results_header = soup.find("h2", string="Recent results for FURIA")
        if not results_header:
            logging.warning("Could not find 'Recent results for FURIA' header.")
            return previous_matches

        recent_results_table = results_header.find_next_sibling("table", class_="match-table")
        if not recent_results_table:
            logging.warning("Could not find recent results table.")
            return previous_matches

        current_event = "Unknown Event"
        for section in recent_results_table.find_all(["thead", "tbody"], recursive=False):
            if section.name == "thead" and section.select_one("tr.event-header-cell"):
                current_event = self._extract_event_name(section)
            elif section.name == "tbody":
                previous_matches.extend(self._extract_previous_matches(section, current_event))


        return previous_matches

    def get_upcoming_matches(self) -> List[UpcomingMatchDTO]:
        soup = self._fetch_page_soup()
        if not soup:
            return []

        upcoming_matches = []
        upcoming_header = soup.find("h2", string="Upcoming matches for FURIA")
        if not upcoming_header:
            logging.warning("Could not find 'Upcoming matches for FURIA' header.")
            return upcoming_matches

        upcoming_results_table = upcoming_header.find_next_sibling("table", class_="match-table")
        if not upcoming_results_table:
            logging.warning("Could not find upcoming matches table.")
            return upcoming_matches

        current_event = "Unknown Event"
        for section in upcoming_results_table.find_all(["thead", "tbody"], recursive=False):
            if section.name == "thead" and section.select_one("tr.event-header-cell"):
                current_event = self._extract_event_name(section)
            elif section.name == "tbody":
                upcoming_matches.extend(self._extract_upcoming_matches(section, current_event))

        return upcoming_matches