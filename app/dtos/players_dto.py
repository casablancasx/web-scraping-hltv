from pydantic import BaseModel


class PlayersDTO(BaseModel):
    player_img: str
    nickname: str
    country: str
    country_img: str