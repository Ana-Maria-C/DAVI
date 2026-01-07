from fastapi import APIRouter, Depends
from app.services.movie_service import MovieService

router = APIRouter(tags=["Analysis & Intelligence"])


def get_service():
    return MovieService()


@router.get("/facets", summary="Get Facet Data for Filtering")
def get_facets(service: MovieService = Depends(get_service)):
    """
    Returns available facets including:
    - Genre Hierarchy
    - Year Range
    - Rating Range
    """
    return service.get_facet_data()
