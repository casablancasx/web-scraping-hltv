from datetime import date

from pydantic import BaseModel


class ChampionshipsDTO(BaseModel):
    days_until_event: int
    event_name: str
    event_img: str
    event_link: str
    start_date: date
    end_date: date
    status: str #ONGOING, UPCOMING




