from pydantic import BaseModel, Field
from typing import List, Optional

class GenreDTO(BaseModel):
    label: str
    uri: Optional[str] = None

class MovieDTO(BaseModel):
    id: str
    title: str
    uri: Optional[str] = None
    genres: List[str] = []
    average_rating: Optional[float] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "1",
                "title": "Toy Story (1995)",
                "genres": ["Adventure", "Animation", "Children"],
                "average_rating": 3.92
            }
        }

class TrendDTO(BaseModel):
    genre: str
    movie_count: int
    average_rating: float
