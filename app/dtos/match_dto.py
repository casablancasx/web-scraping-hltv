from pydantic import BaseModel
from datetime import date
from typing import Optional


class PreviousMatchDTO(BaseModel):
    team1_logo: str
    team1_name: str
    team1_score: int
    team2_logo: str
    team2_name: str
    team2_score: int
    match_date: date
    event_name : str
    result: Optional[str] = None


class UpcomingMatchDTO(BaseModel):
    team1_logo: str
    team1: str
    team2_logo: str
    team2: str
    match_time: date
    event_name: Optional[str] = None

