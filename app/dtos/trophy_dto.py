from pydantic import BaseModel


class TrophyDTO(BaseModel):
    event_name: str
    trophy_img: str
    hltv_event_link: str
