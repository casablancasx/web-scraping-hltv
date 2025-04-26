from bs4 import BeautifulSoup
import cloudscraper
from app.dtos.team_info_dto import InfoTeamDTO, PlayerDTO

class InfoTeamService:
    BASE_URL = "https://www.hltv.org/team/8297/furia"

    def __init__(self):
        self.scraper = cloudscraper.create_scraper()

    def get_team_info(self) -> InfoTeamDTO:
        soup = self._fetch_page_soup()

        logo = self._extract_logo(soup)
        team_name = self._extract_team_name(soup)
        country = self._extract_country(soup)
        valve_rank = self._extract_valve_rank(soup)
        world_rank = self._extract_world_rank(soup)
        coach = self._extract_coach(soup)
        twitter, instagram, twitch = self._extract_social_links(soup)
        players = self._extract_players(soup)

        return InfoTeamDTO(
            logo=logo,
            team_name=team_name,
            country=country,
            valve_rank=valve_rank,
            world_rank=world_rank,
            coach=coach,
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

    def _extract_coach(self, soup: BeautifulSoup) -> str:
        coach_tag = soup.select_one('.profile-team-stat:has(b:contains("Coach")) a span.bold')
        return coach_tag.text.strip().strip("'") if coach_tag else ""

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

    def _extract_players(self, soup: BeautifulSoup) -> list[PlayerDTO]:
        player_rows = soup.select('.players-table tbody tr')
        players = []

        for row in player_rows:
            player_img = row.select_one('.playersBox-img-wrapper img')['src']
            nickname = row.select_one('.playersBox-playernick div.text-ellipsis').text.strip()
            nationality = row.select_one('.playersBox-playernick img.flag')['title']
            status = row.select_one('.status-cell .player-status').text.strip()
            rating_text = row.select_one('.rating-cell').text.strip()
            rating = float(rating_text.split()[0])

            players.append(PlayerDTO(
                player_img=player_img,
                nickname=nickname,
                nationality=nationality,
                status=status,
                rating=rating
            ))

        return players
