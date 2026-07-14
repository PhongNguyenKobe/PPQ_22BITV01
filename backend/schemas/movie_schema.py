from pydantic import BaseModel

class Movie(BaseModel):
    id: int
    title: str
    genre: str
    duration: int
    rating: float
    poster: str