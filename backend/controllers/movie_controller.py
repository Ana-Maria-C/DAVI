from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from services.movie_service import movie_service

router = APIRouter(
    prefix="/api",
    tags=["Movies & Stats"]
)

@router.get("/stats", summary="Get Graph Statistics")
def get_stats():
    """Returns total counts of movies, users, genres, and ratings."""
    return movie_service.get_stats()

@router.get("/movies/search", summary="Search Movies")
def search_movies(
    genre: Optional[str] = None, 
    limit: int = 20, 
    offset: int = 0
):
    """
    Search movies by Genre pattern (regex).
    Validates if the genre exists in the ontology.
    """
    try:
        return movie_service.search_movies(genre, limit, offset)
    except ValueError as e:
        # Ontology Validation Failed
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/trends", summary="Get Trends (Computation Extension)")
def get_trends():
    """
    Extension: Trend Computations.
    Returns average ratings and counts distribution per genre.
    """
    return movie_service.get_genre_trends()

@router.get("/movies/recommend", summary="Get Recommendations")
def recommend_movies(movie_id: int):
    """
    Get generic content-based recommendations for a movie ID.
    Extension: Intelligent Filtering.
    """
    result = movie_service.recommend_movies(movie_id)
    if not result:
        raise HTTPException(status_code=404, detail="Movie not found or no data")
    return result
