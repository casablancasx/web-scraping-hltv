from bs4 import BeautifulSoup, Tag
from cloudscraper import CloudScraper
from typing import List, Optional, Tuple

from app.dtos.coach_dto import CoachInfoDTO
from app.dtos.player_dto import DetailedPlayerDTO
from app.dtos.team_info_dto import InfoTeamDTO
from app.config import Settings
from app.dtos.trophy_dto import TrophyDTO


class InfoTeamService:

    def __init__(self, scraper: CloudScraper, settings: Settings):
        self.scraper = scraper
        self.base_url = settings.furia_hltv_url

    def _fetch_page_soup(self) -> BeautifulSoup:
        try:
            response = self.scraper.get(self.base_url)
            response.raise_for_status()
            return BeautifulSoup(response.content, "html.parser")
        except Exception as e:
            print(f"Error fetching page {self.base_url}: {e}")
            raise

    def _safe_get_text(self, tag: Optional[Tag], default: str = "") -> str:
        return tag.text.strip() if tag else default

    def _safe_get_attr(self, tag: Optional[Tag], attr: str, default: str = "") -> str:
        return tag[attr] if tag and tag.has_attr(attr) else default

    def _safe_parse_int(self, text: str, default: int = 0) -> int:
        try:
            return int(text.replace("#", "").strip())
        except (ValueError, AttributeError):
            return default

    def _safe_parse_float(self, text: str, default: float = 0.0) -> float:
        try:
            return float(text.split()[0])
        except (ValueError, AttributeError, IndexError):
            return default

    def _extract_basic_info(self, soup: BeautifulSoup) -> Tuple[str, str, str]:
        team_logo_tag = soup.select_one(".profile-team-logo-container img")
        team_logo = self._safe_get_attr(team_logo_tag, "src")

        team_name_tag = soup.select_one("h1.profile-team-name")
        team_name = self._safe_get_text(team_name_tag)

        country_tag = soup.select_one(".team-country img")
        country = self._safe_get_attr(country_tag, "alt")

        return team_logo, team_name, country

    def _extract_rankings(self, soup: BeautifulSoup) -> Tuple[int, int, int]:
        valve_rank_tag = soup.select_one(".profile-team-stat:-soup-contains('Valve ranking') .right a")
        valve_rank = self._safe_parse_int(self._safe_get_text(valve_rank_tag))

        world_rank_tag = soup.select_one(".profile-team-stat:-soup-contains('World ranking') .right a")
        world_rank = self._safe_parse_int(self._safe_get_text(world_rank_tag))

        weeks_top30_tag = soup.select_one(".profile-team-stat:-soup-contains('Weeks in top30 for core') .right")
        weeks_in_top_30 = self._safe_parse_int(self._safe_get_text(weeks_top30_tag))

        return valve_rank, world_rank, weeks_in_top_30

    def _extract_social_media(self, soup: BeautifulSoup) -> Tuple[str, str, str]:
        twitter, twitch, instagram = "", "", ""
        social_links = soup.select(".socialMediaButtons a")
        for link in social_links:
            href = self._safe_get_attr(link, "href")
            if "twitter.com" in href:
                twitter = href
            elif "twitch.tv" in href:
                twitch = href
            elif "instagram.com" in href:
                instagram = href
        return twitter, twitch, instagram

    def _extract_players(self, soup: BeautifulSoup) -> List[DetailedPlayerDTO]:
        players = []
        players_table = soup.select_one("table.table-container.players-table")
        if not players_table:
            print("Warning: Players table not found.")
            return players

        player_rows = players_table.select("tbody tr")
        if not player_rows:
            print("Warning: No player rows found in the table.")
            return players

        for row in player_rows:
            player_link_tag = row.select_one("td.playersBox-first-cell a.playersBox-playernick-image")
            if not player_link_tag:
                continue

            img_tag = player_link_tag.select_one(".playersBox-img-wrapper img.playerBox-bodyshot")
            nickname_div = player_link_tag.select_one(".playersBox-playernick .text-ellipsis")
            nationality_tag = player_link_tag.select_one(".playersBox-playernick img.flag")

            status_tag = row.select_one("td .player-status")

            center_cells = row.select("td .center-cell.opacity-cell")
            time_on_team_tag = center_cells[0] if len(center_cells) > 0 else None
            maps_played_tag = center_cells[1] if len(center_cells) > 1 else None

            rating_tag = row.select_one("td .rating-cell")

            player_img = self._safe_get_attr(img_tag, "src")
            nickname = self._safe_get_text(nickname_div)
            nationality = self._safe_get_attr(nationality_tag, "alt")
            status = self._safe_get_text(status_tag)

            time_on_team_raw = self._safe_get_text(time_on_team_tag)
            time_on_team = ' '.join(time_on_team_raw.split())

            maps_played_text = self._safe_get_text(maps_played_tag)
            maps_played = self._safe_parse_int(maps_played_text)

            rating_text_raw = self._safe_get_text(rating_tag)
            rating_text = rating_text_raw.split()[0] if rating_text_raw else "0.0"
            rating = self._safe_parse_float(rating_text)

            if nickname:
                player_dto = DetailedPlayerDTO(
                    player_img=player_img,
                    nickname=nickname,
                    nationality=nationality,
                    status=status,
                    rating=rating,
                    maps_played=maps_played,
                    time_on_team=time_on_team
                )
                players.append(player_dto)
            else:
                print(f"Warning: Skipping row, could not extract nickname. Row HTML: {row}")

        return players

    def _extract_coach(self, soup: BeautifulSoup) -> Optional[CoachInfoDTO]:
        coach_table = soup.select_one("table.table-container.coach-table")
        if not coach_table:
            print("Warning: Coach table not found.")
            return None

        coach_row = coach_table.select_one("tbody tr")
        if not coach_row:
            print("Warning: Coach row not found in the table.")
            return None

        coach_link_tag = coach_row.select_one("td.playersBox-first-cell a.playersBox-playernick-image")
        if not coach_link_tag:
            print("Warning: Coach link tag not found.")
            return None

        img_tag = coach_link_tag.select_one(".playersBox-img-wrapper img.playerBox-bodyshot")
        nickname_div = coach_link_tag.select_one(".playersBox-playernick .text-ellipsis")

        center_cells = coach_row.select("td .center-cell.opacity-cell")
        time_on_team_tag = center_cells[0] if len(center_cells) > 0 else None
        maps_coached_tag = center_cells[1] if len(center_cells) > 1 else None
        trophies_tag = center_cells[2] if len(center_cells) > 2 else None

        winrate_tag = coach_row.select_one("td .rating-cell")

        coach_img = self._safe_get_attr(img_tag, "src")
        nickname = self._safe_get_text(nickname_div)

        time_on_team_raw = self._safe_get_text(time_on_team_tag)
        time_on_team = ' '.join(time_on_team_raw.split())

        maps_coached_text = self._safe_get_text(maps_coached_tag)
        maps_coached = self._safe_parse_int(maps_coached_text)

        trophies_text = self._safe_get_text(trophies_tag)
        trophies_won = self._safe_parse_int(trophies_text)

        winrate = self._safe_get_text(winrate_tag)

        if nickname:
            return CoachInfoDTO(
                coach_img=coach_img,
                nickname=nickname,
                maps_coached=maps_coached,
                trophies_won=trophies_won,
                time_on_team=time_on_team,
                winrate=winrate
            )
        else:
            print(f"Warning: Could not extract coach nickname. Row HTML: {coach_row}")
            return None

    def _extract_trophies(self, soup: BeautifulSoup) -> List[TrophyDTO]:
        """Extracts the list of trophies won by the team."""
        trophies = []
        trophy_section = soup.select_one(".trophySection")
        if not trophy_section:
            print("Warning: Trophy section not found.")
            return trophies

        trophy_links = trophy_section.select("a.trophy")
        for link in trophy_links:
            event_link_raw = self._safe_get_attr(link, "href")
            event_link = f"https://www.hltv.org{event_link_raw}" if event_link_raw.startswith('/') else event_link_raw

            description_span = link.select_one("span.trophyDescription")
            img_tag = link.select_one(".trophyIcon")

            event_name = self._safe_get_attr(description_span, "title")
            if not event_name:
                 event_name = self._safe_get_attr(img_tag, "title")

            icon_url = self._safe_get_attr(img_tag, "src")

            if event_name:
                trophies.append(TrophyDTO(
                    event_name=event_name.strip(),
                    trophy_img=icon_url,
                    hltv_event_link=event_link
                ))
            else:
                print(f"Warning: Could not extract event name for trophy: {link}")

        return trophies

    def get_team_info(self) -> InfoTeamDTO:
        soup = self._fetch_page_soup()

        team_logo, team_name, country = self._extract_basic_info(soup)
        valve_rank, world_rank, weeks_in_top_30 = self._extract_rankings(soup)
        twitter, twitch, instagram = self._extract_social_media(soup)
        players = self._extract_players(soup)
        coach_info = self._extract_coach(soup)
        trophies = self._extract_trophies(soup)

        return InfoTeamDTO(
            team_logo=team_logo,
            team_name=team_name,
            country=country,
            valve_rank=valve_rank,
            world_rank=world_rank,
            weeks_in_top_30=weeks_in_top_30,
            twitter=twitter,
            twitch=twitch,
            instagram=instagram,
            players=players,
            coach=coach_info,
            trophies=trophies
        )