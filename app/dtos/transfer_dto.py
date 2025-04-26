from pydantic import BaseModel
from typing import Optional
from datetime import date

class TransferDTO(BaseModel):
    nickname: str
    role: str
    action: str
    from_team: Optional[str]
    to_team: Optional[str]
    date: date