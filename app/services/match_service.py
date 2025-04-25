import cloudscraper
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List
from app.dtos.match_dto import PreviousMatchDTO, UpcomingMatchDTO


class MatchService:
    def __init__(self):
        self.url = "https://www.hltv.org/team/9565/vitality"
        self.scraper = cloudscraper.create_scraper()

    def _fetch_html_soup(self) -> BeautifulSoup:
        response = self.scraper.get(self.url)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")

    def _get_event_name(self, table) -> str:
        event_link = table.select_one("thead tr.event-header-cell a.a-reset")
        return event_link.text.strip() if event_link else ""

    def _parse_match_rows(self, table) -> List[dict]:
        event_name = self._get_event_name(table)
        matches = []

        for row in table.select("tbody tr.team-row"):
            date_element = row.select_one("td.date-cell span[data-time-format='dd/MM/yyyy']")
            match_date = datetime.strptime(date_element.text.strip(), "%d/%m/%Y").date() if date_element else None

            # Team 1 info
            team1_name_element = row.select_one("a.team-name.team-1")
            team1_name = team1_name_element.text.strip() if team1_name_element else "Unknown"

            team1_logo_container = row.select_one("div.team-flex span.team-logo-container")
            team1_logo_img = team1_logo_container.select_one("img") if team1_logo_container else None
            team1_logo = team1_logo_img["src"] if team1_logo_img else ""

            # Team 2 info
            team2_name_element = row.select_one("a.team-name.team-2")
            team2_name = team2_name_element.text.strip() if team2_name_element else "Unknown"

            team2_logo_container = row.select("div.team-flex span.team-logo-container")
            team2_logo_img = team2_logo_container[1].select_one("img") if len(team2_logo_container) > 1 else None
            team2_logo = team2_logo_img["src"] if team2_logo_img else ""

            # Scores
            score1_element = row.select_one("td.team-center-cell span.score:nth-of-type(1)")
            score2_element = row.select_one("td.team-center-cell span.score:nth-of-type(2)")
            score1 = int(score1_element.text) if score1_element and score1_element.text.isdigit() else 0
            score2 = int(score2_element.text) if score2_element and score2_element.text.isdigit() else 0

            # Match link
            match_link_element = row.select_one("a.stats-button, a.matchpage-button")
            match_link = match_link_element["href"] if match_link_element else ""

            matches.append({
                "event": event_name,
                "date": match_date,
                "team1": team1_name,
                "team1_logo": team1_logo,
                "team2": team2_name,
                "team2_logo": team2_logo,
                "score1": score1,
                "score2": score2,
                "link": match_link,
            })

        return matches

    def _parse_upcoming_matches(self, soup: BeautifulSoup) -> List[dict]:
        upcoming_table = soup.select_one("#matchesBox table.match-table")
        return self._parse_match_rows(upcoming_table)

    def _parse_previous_matches(self, soup: BeautifulSoup) -> List[dict]:
        all_match_tables = soup.select("table.match-table")
        recent_matches_table = all_match_tables[1] if len(all_match_tables) > 1 else None
        return self._parse_match_rows(recent_matches_table) if recent_matches_table else []

    def get_upcoming_matches(self) -> List[UpcomingMatchDTO]:
        soup = self._fetch_html_soup()
        upcoming_matches_data = self._parse_upcoming_matches(soup)

        return [
            UpcomingMatchDTO(
                team1_logo=match["team1_logo"],
                team1=match["team1"],
                team2_logo=match["team2_logo"],
                team2=match["team2"],
                match_time=match["date"],
                event_name=match["event"],
            )
            for match in upcoming_matches_data
        ]

    def get_previous_matches(self) -> List[PreviousMatchDTO]:
        soup = self._fetch_html_soup()
        previous_matches_data = self._parse_previous_matches(soup)

        return [
            PreviousMatchDTO(
                team1_logo=match["team1_logo"],
                team1=match["team1"],
                score1=match["score1"],
                team2_logo=match["team2_logo"],
                team2=match["team2"],
                score2=match["score2"],
                date=match["date"],
                event_name=match["event"],
            )
            for match in previous_matches_data
        ]
