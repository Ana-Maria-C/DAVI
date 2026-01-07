from fastapi import APIRouter, Depends
from app.services.movie_service import MovieService
from app.services.analysis_service import AnalysisService

router = APIRouter(tags=["Analysis & Intelligence"])


def get_service():
    return MovieService()


def get_analysis_service():
    return AnalysisService()


@router.get("/facets", summary="Get Facet Data for Filtering")
def get_facets(service: MovieService = Depends(get_service)):
    """
    Returns available facets including:
    - Genre Hierarchy
    - Year Range
    - Rating Range
    """
    return service.get_facet_data()


@router.get("/stats", summary="Get Statistical Analysis")
def get_stats(service: AnalysisService = Depends(get_analysis_service)):
    """
    Returns aggregated statistics and distributions.
    """
    return service.get_statistics()
