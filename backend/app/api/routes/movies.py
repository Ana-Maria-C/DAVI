from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from app.services.movie_service import MovieService
from app.models.movie_models import MovieDTO, TrendDTO

router = APIRouter(tags=["Movies & Analytics"])

def get_service():
    return MovieService()

@router.get("/stats", summary="Get Graph Statistics")
def get_stats(service: MovieService = Depends(get_service)):
    return service.get_stats()

@router.get("/movies/search", response_model=List[MovieDTO], summary="Search Movies")
def search_movies(
    genre: Optional[str] = None, 
    limit: int = 20, 
    offset: int = 0,
    service: MovieService = Depends(get_service)
):
    try:
        return service.search_movies(genre, limit, offset)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/trends", response_model=List[TrendDTO], summary="Get Trends")
def get_trends(service: MovieService = Depends(get_service)):
    return service.get_trends()

@router.get("/movies/compare", summary="Compare two movies (Extension 2)")
def compare_movies(m1: int, m2: int, service: MovieService = Depends(get_service)):
    """
    Compares two movies and returns their common attributes (Intersection).
    """
    return service.compare_movies(m1, m2)

@router.get("/movies/graph", summary="Get Graph Visualization Data (Extension 3)")
def get_graph(service: MovieService = Depends(get_service)):
    """
    Returns data in {nodes: [], links: []} format for D3.js visualization.
    """
    return service.get_graph_visualization()
