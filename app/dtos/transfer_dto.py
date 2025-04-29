from pydantic import BaseModel
from typing import Optional
from datetime import date

class TransferDTO(BaseModel):
    player_img: str
    nickname: str
    role: str
    action: str
    from_team: Optional[str]
    from_team_img: Optional[str]
    to_team: Optional[str]
    to_team_img: Optional[str]
    date: date