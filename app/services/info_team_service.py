from bs4 import BeautifulSoup
import cloudscraper
from app.dtos.team_info_dto import InfoTeamDTO, PlayerDTO


class InfoTeamService:
    BASE_URL = "https://www.hltv.org/team/8297/furia"

    def __init__(self):
        self.scraper = cloudscraper.create_scraper()

    def _fetch_page_soup(self):
        response = self.scraper.get(self.BASE_URL)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")

    def get_team_info(self) -> InfoTeamDTO:
        soup = self._fetch_page_soup()

        # Logo, team name and country
        logo = soup.select_one('.profile-team-logo-container img')['src']
        team_name = soup.select_one('.profile-team-name').text.strip()
        country = soup.select_one('.team-country img')['title']

        # Ranks
        valve_rank = int(soup.select_one('.profile-team-stat:has(img[alt="Valve logo"]) .right a').text.strip().replace('#', ''))
        world_rank = int(soup.select_one('.profile-team-stat:has(img[alt="HLTV logo"]) .right a').text.strip().replace('#', ''))

        # Coach
        coach = soup.select_one('.profile-team-stat:has(b:contains("Coach")) a span.bold').text.strip().strip("'")

        # Social Media
        social_links = soup.select('.socialMediaButtons a')
        twitter = ""
        instagram = ""
        twitch = ""
        for link in social_links:
            href = link['href']
            if "twitter.com" in href:
                twitter = href
            elif "instagram.com" in href:
                instagram = href
            elif "twitch.tv" in href:
                twitch = href

        # Players
        player_rows = soup.select('.players-table tbody tr')
        players = []
        for row in player_rows:
            img = row.select_one('.playersBox-img-wrapper img')['src']
            nickname = row.select_one('.playersBox-playernick div.text-ellipsis').text.strip()
            nationality = row.select_one('.playersBox-playernick img.flag')['title']
            status = row.select_one('.status-cell .player-status').text.strip()





            rating_text = row.select_one('.rating-cell').text.strip()
            rating = float(rating_text.split()[0])

            players.append(PlayerDTO(
                player_img=img,
                nickname=nickname,
                nationality=nationality,
                status=status,
                rating=rating
            ))

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
