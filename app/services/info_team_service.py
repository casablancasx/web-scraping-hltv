from bs4 import BeautifulSoup
import cloudscraper
from app.dtos.team_info_dto import InfoTeamDTO, PlayersDTO


class InfoTeamService:
    def __init__(self):
        self.scraper = cloudscraper.create_scraper()
        self.url = "https://www.hltv.org/team/8297/furia"

    def get_team_info(self) -> InfoTeamDTO:
        response = self.scraper.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")

        profile_box = soup.find("div", class_="profileTopBox")

        name = profile_box.find("h1", class_="profile-team-name").text.strip()

        logo = profile_box.find("div", class_="profile-team-logo-container").find("img")["src"]

        country_div = profile_box.find("div", class_="team-country")
        country = country_div.text.strip()

        valve_rank_text = profile_box.find_all("div", class_="profile-team-stat")[0]
        valve_rank_link = valve_rank_text.find("a")
        valve_rank = int(valve_rank_link.text.replace("#", "").strip()) if valve_rank_link else 0

        world_rank_text = profile_box.find_all("div", class_="profile-team-stat")[1]
        world_rank_link = world_rank_text.find("a")
        world_rank = int(world_rank_link.text.replace("#", "").strip()) if world_rank_link else 0

        coach_name = ""
        for stat in profile_box.find_all("div", class_="profile-team-stat"):
            if stat.find("b") and "Coach" in stat.find("b").text:
                coach_link = stat.find("a")
                if coach_link:
                    coach_name = coach_link.text.strip()

        players = []
        players_box = soup.find("div", class_="bodyshot-team")
        if players_box:
            for player in players_box.find_all("a", class_="col-custom"):
                player_img_tag = player.find("img", class_="bodyshot-team-img")
                nickname_tag = player.find("span", class_="bold")
                country_img_tag = player.find("img", class_="flag")

                player_img = player_img_tag["src"] if player_img_tag else ""
                name_player = nickname_tag.text.strip() if nickname_tag else ""
                country_player = country_img_tag["title"] if country_img_tag else ""


                players.append(
                    PlayersDTO(
                        player_img=player_img,
                        nickname=name_player,
                        country=country_player,
                    )
                )

        team_info = InfoTeamDTO(
            logo=logo,
            name=name,
            country=country,
            valve_rank=valve_rank,
            world_rank=world_rank,
            coach=coach_name,
            players=players
        )

        return team_info
