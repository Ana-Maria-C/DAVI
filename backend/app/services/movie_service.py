from typing import List, Optional
from app.repositories.movie_repository import MovieRepository
from app.models.movie_models import MovieDTO, TrendDTO, GenreDTO

class MovieService:
    def __init__(self):
        self.repository = MovieRepository()

    def get_stats(self):
        return self.repository.get_stats()

    def search_movies(self, genre: Optional[str], limit: int, offset: int) -> List[MovieDTO]:
        if genre and not self.repository.check_genre_exists(genre):
             raise ValueError(f"Genre '{genre}' is not defined in the Knowledge Graph.")

        raw_results = self.repository.search_movies(genre, limit, offset)
        
        movies = []
        for row in raw_results:
            movies.append(MovieDTO(
                id=row["mid"]["value"] if "mid" in row else "",
                title=row["title"]["value"] if "title" in row else "Unknown",
                genres=row["genres"]["value"].split("|") if "genres" in row else [],
                uri=None 
            ))
        return movies

    def get_trends(self) -> List[TrendDTO]:
        raw_results = self.repository.get_trends()
        trends = []
        for row in raw_results:
            trends.append(TrendDTO(
                genre=row["gLabel"]["value"],
                movie_count=int(row["movieCount"]["value"]),
                average_rating=float(row["avgRating"]["value"])
            ))
        return trends

    def compare_movies(self, id1: int, id2: int):
        return self.repository.compare_movies(str(id1), str(id2))

    def get_graph_visualization(self):
        raw_data = self.repository.get_graph_data(limit=30)
        
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
            
        return {
            "nodes": list(nodes.values()),
            "links": links
        }
