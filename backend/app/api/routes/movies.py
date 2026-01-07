from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from app.services.movie_service import MovieService
from app.models.movie_models import MovieDTO, TrendDTO

router = APIRouter(tags=["Movies & Analytics"])


def get_service():
    return MovieService()


@router.get("/stats", summary="Get Graph Statistics")
def get_stats(service: MovieService = Depends(get_service)):
    return service.get_stats()


@router.get("/movies", response_model=List[MovieDTO], summary="Get All Movies")
def get_movies(
    limit: int = 20,
    offset: int = 0,
    sort: str = "title",
    service: MovieService = Depends(get_service),
):
    return service.get_movies(limit, offset, sort)


@router.get("/movies/search", response_model=List[MovieDTO], summary="Search Movies")
def search_movies(
    genre: Optional[str] = None,
    year_min: Optional[int] = None,
    year_max: Optional[int] = None,
    rating_min: Optional[float] = None,
    rating_max: Optional[float] = None,
    sort: str = "title",
    limit: int = 20,
    offset: int = 0,
    service: MovieService = Depends(get_service),
):
    try:
        return service.search_movies(
            genre, year_min, year_max, rating_min, rating_max, sort, limit, offset
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/trends", response_model=List[TrendDTO], summary="Get Trends")
def get_trends(service: MovieService = Depends(get_service)):
    return service.get_trends()


@router.get("/movies/compare", summary="Compare multiple movies")
def compare_movies(
    ids: List[int] = Query(...), service: MovieService = Depends(get_service)
):
    """
    Compares selected movies and returns their details (Title, Year, Rating, Reviews).
    """
    return service.compare_movies(ids)


@router.get("/movies/graph", summary="Get Graph Visualization Data (Extension 3)")
def get_graph(service: MovieService = Depends(get_service)):
    """
    Returns data in {nodes: [], links: []} format for D3.js visualization.
    """
    return service.get_graph_visualization()


@router.get("/genres", summary="Get Genre Hierarchy (For Smart Filters)")
def get_genres(service: MovieService = Depends(get_service)):
    """
    Returns genres grouped by their super-categories (Emotional, Exciting, etc.).
    """
    return service.get_genres()


from app.models.movie_models import MovieCreate, MovieUpdate, RatingCreate


@router.post("/movies", status_code=201, summary="Create a new Movie")
def create_movie(movie: MovieCreate, service: MovieService = Depends(get_service)):
    try:
        new_id = service.create_movie(movie.title, movie.genres)
        return {"id": new_id, "message": "Movie created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/movies/{movie_id}", summary="Get Movie Details by ID")
def get_movie(movie_id: str, service: MovieService = Depends(get_service)):
    movie = service.get_movie_by_id(movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie


@router.put("/movies/{movie_id}", summary="Update Movie")
def update_movie(
    movie_id: str, movie: MovieUpdate, service: MovieService = Depends(get_service)
):
    service.update_movie(movie_id, movie.title, movie.genres)
    return {"message": "Movie updated successfully"}


@router.delete("/movies/{movie_id}", summary="Delete Movie (Cascading)")
def delete_movie(movie_id: str, service: MovieService = Depends(get_service)):
    service.delete_movie(movie_id)
    return {"message": "Movie deleted successfully"}


@router.post("/ratings", status_code=201, summary="Add a Rating")
def add_rating(rating: RatingCreate, service: MovieService = Depends(get_service)):
    service.add_rating(rating.user_id, rating.movie_id, rating.value)
    return {"message": "Rating added successfully"}
