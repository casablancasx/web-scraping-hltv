from pydantic import BaseModel


class CoachInfoDTO(BaseModel):
    coach_img: str
    nickname: str
    maps_played: int
    trophies_won: int
    winrante: str