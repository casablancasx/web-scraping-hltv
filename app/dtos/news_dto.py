from pydantic import BaseModel


class NewsDTO(BaseModel):
    title: str
    source_link: str