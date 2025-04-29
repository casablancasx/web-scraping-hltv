from bs4 import BeautifulSoup
import cloudscraper
import os

from app.dtos.player_dto import ActivePlayerDTO
from app.dtos.team_info_dto import InfoTeamDTO

class InfoTeamService:
    BASE_URL = os.getenv("FURIA_HLTV_URL", "https://www.hltv.org/team/8297/furia")

    def __init__(self):
        self.scraper = cloudscraper.create_scraper()

    def get_team_info(self) -> InfoTeamDTO:
        soup = self._fetch_page_soup()

        logo = self._extract_logo(soup)
        team_name = self._extract_team_name(soup)
        country = self._extract_country(soup)
        valve_rank = self._extract_valve_rank(soup)
        world_rank = self._extract_world_rank(soup)
        coach, coach_nationality = self._extract_coach_info(soup)
        twitter, instagram, twitch = self._extract_social_links(soup)
        players = self._extract_players(soup)

        return InfoTeamDTO(
            team_logo=logo,
            team_name=team_name,
            country=country,
            valve_rank=valve_rank,
            world_rank=world_rank,
            coach=coach,
            coach_nationality=coach_nationality,
            twitter=twitter,
            instagram=instagram,
            twitch=twitch,
            players=players
        )

    def _fetch_page_soup(self) -> BeautifulSoup:
        response = self.scraper.get(self.BASE_URL)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")

    def _extract_logo(self, soup: BeautifulSoup) -> str:
        return soup.select_one('.profile-team-logo-container img')['src']

    def _extract_team_name(self, soup: BeautifulSoup) -> str:
        return soup.select_one('.profile-team-name').text.strip()

    def _extract_country(self, soup: BeautifulSoup) -> str:
        return soup.select_one('.team-country img')['title']

    def _extract_valve_rank(self, soup: BeautifulSoup) -> int:
        valve_rank_text = soup.select_one('.profile-team-stat:has(img[alt="Valve logo"]) .right a').text.strip()
        return int(valve_rank_text.replace('#', ''))

    def _extract_world_rank(self, soup: BeautifulSoup) -> int:
        world_rank_text = soup.select_one('.profile-team-stat:has(img[alt="HLTV logo"]) .right a').text.strip()
        return int(world_rank_text.replace('#', ''))

    def _extract_coach_info(self, soup: BeautifulSoup) -> tuple[str, str]:
        coach_section = soup.select_one('.profile-team-stat:has(b:contains("Coach")) a')
        if not coach_section:
            return "", ""

        coach_img = coach_section.select_one('img.flag')
        coach_nationality = coach_img['title'] if coach_img else ""

        coach_name_tag = coach_section.select_one('span.bold')
        coach_nickname = coach_name_tag.text.strip().strip("'") if coach_name_tag else ""

        return coach_nickname, coach_nationality

    def _extract_social_links(self, soup: BeautifulSoup) -> tuple[str, str, str]:
        twitter = instagram = twitch = ""
        social_links = soup.select('.socialMediaButtons a')

        for link in social_links:
            href = link['href']
            if "twitter.com" in href:
                twitter = href
            elif "instagram.com" in href:
                instagram = href
            elif "twitch.tv" in href:
                twitch = href

        return twitter, instagram, twitch

    def _extract_players(self, soup: BeautifulSoup) -> list[ActivePlayerDTO]:
        player_cards = soup.select('.bodyshot-team a.col-custom')
        players = []

        for card in player_cards:
            player_img_tag = card.select_one('.bodyshot-team-img')
            nickname_tag = card.select_one('.playerFlagName .bold')
            nationality_tag = card.select_one('.playerFlagName img.flag')

            player_img = player_img_tag['src'] if player_img_tag else ""
            nickname = nickname_tag.text.strip() if nickname_tag else ""
            nationality = nationality_tag['title'] if nationality_tag else ""

            players.append(ActivePlayerDTO(
                player_img=player_img,
                nickname=nickname,
                nationality=nationality
            ))

        return players


