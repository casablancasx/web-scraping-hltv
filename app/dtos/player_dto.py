from pydantic import BaseModel


class PlayerDTO(BaseModel):
    player_img: str
    nickname: str
    nationality: str
    status: str
    rating: float