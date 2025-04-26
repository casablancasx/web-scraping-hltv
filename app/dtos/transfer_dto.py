from pydantic import BaseModel
from typing import Optional
from datetime import date

class TransferDTO(BaseModel):
    nickname: str
    role: str  # "Player" ou "Coach"
    action: str  # "transfer", "bench", "join", "part ways"
    from_team: Optional[str]  # pode ser None ou "no team"
    to_team: Optional[str]    # pode ser None
    date: date