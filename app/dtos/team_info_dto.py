from pydantic import BaseModel

from app.dtos.player_dto import PlayerDTO


class InfoTeamDTO(BaseModel):
    team_logo: str
    team_name: str
    country: str
    valve_rank: int
    world_rank: int
    coach: str
    coach_nationality: str = ""
    twitter: str = ""
    instagram: str = ""
    twitch: str = ""
    players: list[PlayerDTO]