from datetime import date

from pydantic import BaseModel


class UpComingChampionshipsDto(BaseModel):
    days_until_event: int
    event_name: str
    event_img: str
    event_link: str
    start_date: date
    end_date: date
    status: str #ONGOING, UPCOMING


class PreviousChampionshipsDto(BaseModel):
    event_name: str
    event_img: str
    event_link: str
    start_date: date
    end_date: date


