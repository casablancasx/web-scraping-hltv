from bs4 import BeautifulSoup
import cloudscraper
from app.dtos.team_info_dto import InfoTeamDTO, PlayersDTO


class InfoTeamService:
    BASE_URL = "https://www.hltv.org/team/8297/furia"

    def __init__(self):
        self.scraper = cloudscraper.create_scraper()

    def get_team_info(self) -> InfoTeamDTO:
        soup = self._fetch_page_soup()

        team_name = self._extract_team_name(soup)
        logo = self._extract_team_logo(soup)
        country = self._extract_country(soup)
        valve_rank = self._extract_rank(soup, index=0)
        world_rank = self._extract_rank(soup, index=1)
        coach = self._extract_coach_name(soup)
        players = self._extract_players(soup)

        return InfoTeamDTO(
            logo=logo,
            team_name=team_name,
            country=country,
            valve_rank=valve_rank,
            world_rank=world_rank,
            coach=coach,
            players=players
        )

    def _fetch_page_soup(self) -> BeautifulSoup:
        response = self.scraper.get(self.BASE_URL)
        response.raise_for_status()
        return BeautifulSoup(response.content, "html.parser")

    def _extract_team_name(self, soup: BeautifulSoup) -> str:
        return soup.select_one("div.profileTopBox h1.profile-team-name").text.strip()

    def _extract_team_logo(self, soup: BeautifulSoup) -> str:
        logo_tag = soup.select_one("div.profileTopBox div.profile-team-logo-container img")
        return logo_tag["src"] if logo_tag else ""

    def _extract_country(self, soup: BeautifulSoup) -> str:
        country_tag = soup.select_one("div.profileTopBox div.team-country")
        return country_tag.text.strip() if country_tag else ""

    def _extract_rank(self, soup: BeautifulSoup, index: int) -> int:
        try:
            rank_tag = soup.select("div.profileTopBox div.profile-team-stat")[index].find("a")
            return int(rank_tag.text.replace("#", "").strip()) if rank_tag else 0
        except (IndexError, AttributeError):
            return 0

    def _extract_coach_name(self, soup: BeautifulSoup) -> str:
        coach_stat = next(
            (stat for stat in soup.select("div.profileTopBox div.profile-team-stat")
             if stat.find("b") and "Coach" in stat.find("b").text),
            None
        )
        coach_link = coach_stat.find("a") if coach_stat else None
        return coach_link.text.strip() if coach_link else ""

    def _extract_players(self, soup: BeautifulSoup) -> list[PlayersDTO]:
        players = []
        players_box = soup.select_one("div.bodyshot-team")

        if not players_box:
            return players

        for player_tag in players_box.select("a.col-custom"):
            player_img = player_tag.select_one("img.bodyshot-team-img")
            nickname = player_tag.select_one("span.bold")
            country_flag = player_tag.select_one("img.flag")

            players.append(
                PlayersDTO(
                    player_img=player_img["src"] if player_img else "",
                    nickname=nickname.text.strip() if nickname else "",
                    country=country_flag["title"] if country_flag else ""
                )
            )
        return players
