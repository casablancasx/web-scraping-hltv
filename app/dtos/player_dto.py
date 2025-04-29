from pydantic import BaseModel


class ActivePlayerDTO(BaseModel):
    player_img: str
    nickname: str
    nationality: str



class DetailedPlayerDTO(BaseModel):
    player_img: str
    nickname: str
    nationality: str
    status: str
    rating: float
    maps_played: int