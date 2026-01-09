from app.repositories.movie_repository import MovieRepository


class AnalysisService:
    def __init__(self):
        self.repository = MovieRepository()

    def get_network_graph_data(self):
        """
        Returns node-link data for visualization.
        """
        raw_data = self.repository.get_graph_data(limit=50)

        nodes = {}
        links = []

        for row in raw_data:
            s = row["s"]["value"]
            o = row["o"]["value"]
            p = row["p"]["value"]

            s_label = row.get("sLabel", {}).get("value", s.split("/")[-1])
            o_label = row.get("oLabel", {}).get("value", o.split("/")[-1])
            s_type = row.get("sType", {}).get("value", "Resource")
            o_type = row.get("oType", {}).get("value", "Resource")

            if s not in nodes:
                nodes[s] = {"id": s, "label": s_label, "group": s_type}

            if o not in nodes:
                nodes[o] = {"id": o, "label": o_label, "group": o_type}

            links.append({"source": s, "target": o, "relationship": p})

        return {"nodes": list(nodes.values()), "links": links}

    def get_statistics(self):
        """
        Returns aggregated statistics:
        - General counts (movies, genres, etc.)
        - Distributions (Genres, Ratings)
        """
        stats = self.repository.get_stats()
        trends = self.repository.get_trends()

        genre_distribution = [
            {
                "name": t.get("gLabel", {}).get("value", "Unknown"),
                "value": int(t.get("movieCount", {}).get("value", 0)),
            }
            for t in trends
        ]

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

    def get_top_reviewed_movies(self, limit=10):
        return self.repository.get_most_reviewed_movies(limit)

    def get_top_rated_movies(self, limit=10, min_reviews=20):
        return self.repository.get_highest_rated_movies(limit, min_reviews)

    def get_yearly_trends_data(self, year):
        return self.repository.get_yearly_trends_data(year)
