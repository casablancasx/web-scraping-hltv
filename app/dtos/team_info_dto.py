from pydantic import BaseModel, HttpUrl
from typing import List, Optional # Import Optional
from .player_dto import DetailedPlayerDTO
from .coach_dto import CoachInfoDTO
from .trophy_dto import TrophyDTO


class InfoTeamDTO(BaseModel):
    team_logo: Optional[HttpUrl | str] = None 
    team_name: str
    country: str
    valve_rank: int
    world_rank: int
    weeks_in_top_30: int
    trophies : List[TrophyDTO]
    twitter: Optional[HttpUrl | str] = None
    twitch: Optional[HttpUrl | str] = None
    instagram: Optional[HttpUrl | str] = None
    players: List[DetailedPlayerDTO]
    coach: Optional[CoachInfoDTO] = None 