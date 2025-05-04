from pydantic import BaseModel




class DetailedPlayerDTO(BaseModel):
    player_img: str
    nickname: str
    nationality: str
    status: str
    rating: float
    maps_played: int
    time_on_team: str