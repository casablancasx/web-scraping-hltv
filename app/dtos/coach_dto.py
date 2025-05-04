from pydantic import BaseModel


class CoachInfoDTO(BaseModel):
    coach_img: str
    nickname: str
    maps_coached: int
    trophies_won: int
    time_on_team: str
    winrate: str 