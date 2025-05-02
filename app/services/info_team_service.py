from bs4 import BeautifulSoup
from cloudscraper import CloudScraper

from app.dtos.player_dto import ActivePlayerDTO
from app.dtos.team_info_dto import InfoTeamDTO
from app.config import Settings # Import Settings

class InfoTeamService:

    def __init__(self, scraper: CloudScraper, settings: Settings):
        self.scraper = scraper
        self.base_url = settings.furia_hltv_url

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
        response = self.scraper.get(self.base_url)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")

    def _extract_logo(self, soup: BeautifulSoup) -> str:
        logo_tag = soup.select_one('.profile-team-logo-container img')
        return logo_tag['src'] if logo_tag and logo_tag.has_attr('src') else "N/A"

    def _extract_team_name(self, soup: BeautifulSoup) -> str:
        name_tag = soup.select_one('.profile-team-name')
        return name_tag.text.strip() if name_tag else "N/A"

    def _extract_country(self, soup: BeautifulSoup) -> str:
        country_tag = soup.select_one('.team-country img')
        return country_tag['title'] if country_tag and country_tag.has_attr('title') else "N/A"

    def _extract_valve_rank(self, soup: BeautifulSoup) -> int:
        rank_tag = soup.select_one('.profile-team-stat:has(img[alt="Valve logo"]) .right a')
        if rank_tag:
            rank_text = rank_tag.text.strip().replace('#', '')
            try:
                return int(rank_text)
            except ValueError:
                return 0
        return 0

    def _extract_world_rank(self, soup: BeautifulSoup) -> int:
        rank_tag = soup.select_one('.profile-team-stat:has(img[alt="HLTV logo"]) .right a')
        if rank_tag:
            rank_text = rank_tag.text.strip().replace('#', '')
            try:
                return int(rank_text)
            except ValueError:
                return 0
        return 0

    def _extract_coach_info(self, soup: BeautifulSoup) -> tuple[str, str]:
        coach_section = soup.select_one('.profile-team-stat:has(b:contains("Coach")) a')
        if not coach_section:
            return "N/A", "N/A"

        coach_img = coach_section.select_one('img.flag')
        coach_nationality = coach_img['title'] if coach_img and coach_img.has_attr('title') else "N/A"

        coach_name_tag = coach_section.select_one('span.bold')
        coach_nickname = coach_name_tag.text.strip().strip("'") if coach_name_tag else "N/A"

        return coach_nickname, coach_nationality

    def _extract_social_links(self, soup: BeautifulSoup) -> tuple[str, str, str]:
        twitter = instagram = twitch = ""
        social_links = soup.select('.socialMediaButtons a')

        for link in social_links:
            href = link.get('href')
            if not href: continue

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
            try:
                player_img_tag = card.select_one('.bodyshot-team-img')
                nickname_tag = card.select_one('.playerFlagName .bold')
                nationality_tag = card.select_one('.playerFlagName img.flag')

                player_img = player_img_tag['src'] if player_img_tag and player_img_tag.has_attr('src') else ""
                nickname = nickname_tag.text.strip() if nickname_tag else "N/A"
                nationality = nationality_tag['title'] if nationality_tag and nationality_tag.has_attr('title') else "N/A"

                players.append(ActivePlayerDTO(
                    player_img=player_img,
                    nickname=nickname,
                    nationality=nationality
                ))
            except Exception as e:
                print(f"Error parsing player card: {e}")
                continue

        return players