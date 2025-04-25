import cloudscraper
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List
from app.dtos.match_dto import PreviousMatchDTO, UpcomingMatchDTO


class MatchService:
    def __init__(self):
        self.url = "https://www.hltv.org/team/8297/furia"
        self.scraper = cloudscraper.create_scraper()

    def get_previous_matches(self) -> List[PreviousMatchDTO]:
        response = self.scraper.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")

        previous_matches = []
        recent_results_table = soup.find("h2", string="Recent results for FURIA").find_next("table")

        current_event = ""
        for section in recent_results_table.find_all(["thead", "tbody"], recursive=False):
            if section.name == "thead":
                event_link = section.find("a")
                if event_link:
                    current_event = event_link.text.strip()
            elif section.name == "tbody":
                for row in section.find_all("tr", class_="team-row"):
                    date_str = row.find("td", class_="date-cell").find("span").text.strip()
                    match_date = datetime.strptime(date_str, "%d/%m/%Y")

                    teams = row.find_all("a", class_="team-name")
                    logos = row.find_all("img", class_="team-logo")
                    scores = row.find("div", class_="score-cell").find_all("span", class_="score")

                    team1 = teams[0].text.strip()
                    team2 = teams[1].text.strip()
                    team1_logo = logos[0]["src"]
                    team2_logo = logos[1]["src"]
                    score1 = int(scores[0].text.strip())
                    score2 = int(scores[1].text.strip())

                    match_dto = PreviousMatchDTO(
                        team1=team1,
                        team2=team2,
                        team1_logo=team1_logo,
                        team2_logo=team2_logo,
                        score1=score1,
                        score2=score2,
                        date=match_date,
                        event_name=current_event
                    )
                    previous_matches.append(match_dto)

        return previous_matches

    def get_upcoming_matches(self) -> List[UpcomingMatchDTO]:
        response = self.scraper.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")

        upcoming_matches = []

        upcoming_header = soup.find("h2", string="Upcoming matches for FURIA")
        if not upcoming_header:
            return upcoming_matches

        current = upcoming_header
        current_event = None

        while True:
            current = current.find_next_sibling()
            if current is None:
                break

            if current.name == "h2":
                break

            if current.name == "table" and "match-table" in current.get("class", []):
                for section in current.find_all(["thead", "tbody"], recursive=False):
                    if section.name == "thead":
                        event_link = section.find("a")
                        if event_link:
                            current_event = event_link.text.strip()
                    elif section.name == "tbody":
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

                            team1 = teams[0].text.strip()
                            team2 = teams[1].text.strip()
                            team1_logo = logos[0]["src"]
                            team2_logo = logos[1]["src"]

                            match_dto = UpcomingMatchDTO(
                                team1=team1,
                                team2=team2,
                                team1_logo=team1_logo,
                                team2_logo=team2_logo,
                                match_time=match_time,
                                event_name=current_event
                            )
                            upcoming_matches.append(match_dto)

        return upcoming_matches




