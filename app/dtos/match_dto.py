from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class PreviousMatchDTO(BaseModel):
    team1: str
    team2: str
    score1: int
    score2: int
    date: datetime

class UpcomingMatchDTO(BaseModel):
    team1: str
    team2: str
    match_time: datetime
    event_name: Optional[str] = None
    stream_link: Optional[str] = None
