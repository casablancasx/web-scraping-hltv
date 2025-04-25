from pydantic import BaseModel
from datetime import date
from typing import Optional


class PreviousMatchDTO(BaseModel):
    team1_logo: str
    team1: str
    score1: int
    team2_logo: str
    team2: str
    score2: int
    date: date
    event_name : str


class UpcomingMatchDTO(BaseModel):
    team1_logo: str
    team1: str
    team2_logo: str
    team2: str
    match_time: date
    event_name: Optional[str] = None

