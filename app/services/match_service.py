from typing import List
from datetime import datetime, date
import re
import cloudscraper
from bs4 import BeautifulSoup
from app.dtos.match_dto import PreviousMatchDTO, UpcomingMatchDTO

class MatchService:
    def __init__(self):
        self.scraper = cloudscraper.create_scraper()
        self.url = "https://www.hltv.org/results?team=8297"

    def get_previous_matches(self) -> List[PreviousMatchDTO]:
        response = self.scraper.get(self.url)
        soup = BeautifulSoup(response.text, "html.parser")

        matches: List[PreviousMatchDTO] = []

        for group in soup.find_all("div", class_="results-sublist"):
            headline = group.find("span", class_="standard-headline")
            if not headline:
                continue
            raw_date = headline.get_text(strip=True)
            cleaned = re.sub(r"^Results for\s+", "", raw_date)
            cleaned = re.sub(r"(\d+)(st|nd|rd|th)", r"\1", cleaned)
            match_date = datetime.strptime(cleaned, "%B %d %Y").date()

            for result in group.find_all("div", class_="result-con"):
                team_cells = result.find_all("td", class_="team-cell")
                if len(team_cells) < 2:
                    continue

                team1 = team_cells[0].find("div", class_="team").get_text(strip=True)
                team2 = team_cells[1].find("div", class_="team").get_text(strip=True)

                score_td = result.find("td", class_="result-score")
                score_spans = score_td.find_all("span")
                score1 = int(score_spans[0].get_text(strip=True))
                score2 = int(score_spans[1].get_text(strip=True))

                matches.append(
                    PreviousMatchDTO(
                        team1=team1,
                        team2=team2,
                        score1=score1,
                        score2=score2,
                        date=match_date
                    )
                )

        return matches


    def get_upcoming_matches(self) -> List[UpcomingMatchDTO]:
        return None
