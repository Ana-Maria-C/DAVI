from app.repositories.movie_repository import MovieRepository


class AnalysisService:
    def __init__(self):
        self.repository = MovieRepository()

    def get_statistics(self):
        """
        Returns aggregated statistics:
        - General counts (movies, genres, etc.)
        - Distributions (Genres, Ratings)
        """
        stats = self.repository.get_stats()
        trends = self.repository.get_trends()

        # Transform trends for frontend (Genre Distribution)
        genre_distribution = [
            {
                "name": t.get("gLabel", {}).get("value", "Unknown"),
                "value": int(t.get("movieCount", {}).get("value", 0)),
            }
            for t in trends
        ]

        # Rating distribution (mocked or aggregated from trends for now if repository doesn't have it directly)
        # Or we can use trends avgRating to show Average Rating per Genre
        avg_rating_per_genre = [
            {
                "name": t.get("gLabel", {}).get("value", "Unknown"),
                "value": float(t.get("avgRating", {}).get("value", 0)),
            }
            for t in trends
        ]

        return {
            "counts": stats,
            "genreDistribution": genre_distribution,
            "genreRatings": avg_rating_per_genre,
        }
