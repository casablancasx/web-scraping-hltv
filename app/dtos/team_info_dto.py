from pydantic import BaseModel

from app.dtos.players_dto import PlayersDTO


class InfoTeamDTO(BaseModel):
    logo: str
    name: str
    country: str
    valve_rank: int
    world_rank: int
    coach: str
    players: list[PlayersDTO]