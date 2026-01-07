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


@router.get("/graph", summary="Get Network Graph Data")
def get_graph(service: AnalysisService = Depends(get_analysis_service)):
    """
    Returns Nodes and Links for Network Visualization.
    """
    return service.get_network_graph_data()


@router.get("/stats", summary="Get Statistical Analysis")
def get_stats(service: AnalysisService = Depends(get_analysis_service)):
    """
    Returns aggregated statistics and distributions.
    """
    return service.get_statistics()


@router.get("/trends/famous", summary="Get Most Famous Movies (Most Reviewed)")
def get_most_famous_movies(
    limit: int = 10, service: AnalysisService = Depends(get_analysis_service)
):
    """
    Returns movies with the highest number of reviews.
    """
    return service.get_top_reviewed_movies(limit)


@router.get("/trends/rated", summary="Get Highest Rated Movies")
def get_highest_rated_movies(
    limit: int = 10,
    min_reviews: int = 20,
    service: AnalysisService = Depends(get_analysis_service),
):
    """
    Returns movies with the highest average rating (with a minimum review threshold).
    """
    return service.get_top_rated_movies(limit, min_reviews)


@router.get("/trends/yearly/{year}", summary="Get Trends for a Specific Year")
def get_yearly_trends(
    year: int, service: AnalysisService = Depends(get_analysis_service)
):
    """
    Returns 'Famous' and 'Best Rated' movies for a specific year.
    """
    return service.get_yearly_trends_data(year)
