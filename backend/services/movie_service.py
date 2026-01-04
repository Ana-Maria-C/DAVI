from typing import Optional, List, Dict, Any
import pyoxigraph
from .rdf_store import rdf_store

class MovieService:
    def __init__(self):
        self.store = rdf_store.store

    def get_stats(self) -> Dict[str, int]:
        """Returns basic stats about the graph."""
        q_movies = "SELECT (COUNT(?s) AS ?count) WHERE { ?s a <http://example.org/movielens/Movie> }"
        q_users = "SELECT (COUNT(?s) AS ?count) WHERE { ?s a <http://example.org/movielens/User> }"
        q_genres = "SELECT (COUNT(?s) AS ?count) WHERE { ?s a <http://example.org/movielens/Genre> }"
        q_ratings = "SELECT (COUNT(?s) AS ?count) WHERE { ?s a <http://example.org/movielens/Rating> }"

        return {
            "movies": self._run_count_query(q_movies),
            "users": self._run_count_query(q_users),
            "genres": self._run_count_query(q_genres),
            "ratings": self._run_count_query(q_ratings)
        }

    def _run_count_query(self, query: str) -> int:
        try:
            res = self.store.query(query)
            for row in res:
                return int(row[0].value)
        except:
            return 0
        return 0

    def _genre_exists(self, genre_label: str) -> bool:
        """Checks if a genre label exists in the graph."""
        # Use regex to be case-insensitive compliant with search
        query = f"""
            ASK {{
                ?g a <http://example.org/movielens/Genre> ;
                   <http://www.w3.org/2000/01/rdf-schema#label> ?label .
                FILTER(REGEX(?label, "^{genre_label}$", "i"))
            }}
        """
        try:
            return self.store.query(query)
        except:
            return False

    def search_movies(self, genre: Optional[str], limit: int, offset: int) -> List[Dict[str, Any]]:
        filter_clauses = []
        if genre:
            # Validate if genre exists in Ontology/Graph
            if not self._genre_exists(genre):
                # Return empty or raise specific error? 
                # User asked for validation notification.
                # raising ValueError which FastAPI can catch or we handle it.
                # Let's return a special structure or raise HTTPException in main.
                # For cleaner service design, we raise an exception.
                raise ValueError(f"Genre '{genre}' is not defined in the Ontology/Knowledge Graph.")
                
            filter_clauses.append(f'?m <http://example.org/movielens/hasGenre> ?g . ?g <http://www.w3.org/2000/01/rdf-schema#label> ?gLabel . FILTER(REGEX(?gLabel, "{genre}", "i"))')
        
        where_body = """
            ?m a <http://example.org/movielens/Movie> .
            ?m <http://schema.org/name> ?title .
            OPTIONAL { ?m <http://example.org/movielens/movieId> ?mid } .
        """
        for clause in filter_clauses:
            where_body += f"\n {clause}"
            
        query = f"""
            SELECT ?mid ?title (GROUP_CONCAT(?gLabel; separator="|") as ?genres)
            WHERE {{
                {where_body}
                OPTIONAL {{ ?m <http://example.org/movielens/hasGenre> ?gx . ?gx <http://www.w3.org/2000/01/rdf-schema#label> ?gLabel }}
            }}
            GROUP BY ?mid ?title
            LIMIT {limit}
            OFFSET {offset}
        """
        
        results = self.store.query(query)
        movies = []
        if isinstance(results, pyoxigraph.QuerySolutions):
            for row in results:
                movies.append({
                    "id": row["mid"].value if row["mid"] else None,
                    "title": row["title"].value if row["title"] else "Unknown",
                    "genres": row["genres"].value.split("|") if row["genres"] else []
                })
        return movies

    def recommend_movies(self, movie_id: int) -> Dict[str, Any]:
        # 1. Get genres
        query_genres = f"""
            SELECT ?gLabel WHERE {{
                ?m <http://example.org/movielens/movieId> {movie_id} .
                ?m <http://example.org/movielens/hasGenre> ?g .
                ?g <http://www.w3.org/2000/01/rdf-schema#label> ?gLabel .
            }}
        """
        genres = []
        try:
            res = self.store.query(query_genres)
            for row in res:
                genres.append(row["gLabel"].value)
        except:
            pass
            
        if not genres:
            return None

        # 2. Find similar
        genre_filter = " ".join([f'"{g}"' for g in genres])
        rec_query = f"""
            SELECT ?mid ?title (COUNT(?sharedG) as ?score)
            WHERE {{
                ?m a <http://example.org/movielens/Movie> .
                ?m <http://schema.org/name> ?title .
                ?m <http://example.org/movielens/movieId> ?mid .
                FILTER (?mid != {movie_id})
                
                ?m <http://example.org/movielens/hasGenre> ?sharedG .
                ?sharedG <http://www.w3.org/2000/01/rdf-schema#label> ?targetGLabel .
                VALUES ?targetGLabel {{ {genre_filter} }}
            }}
            GROUP BY ?mid ?title
            ORDER BY DESC(?score)
            LIMIT 10
        """
        
        recommendations = []
        try:
            res = self.store.query(rec_query)
            for row in res:
                 recommendations.append({
                    "id": row["mid"].value,
                    "title": row["title"].value,
                    "score": row["score"].value
                })
        except Exception as e:
            raise e
            
        return {
            "source_movie_id": movie_id,
            "source_genres": genres,
            "recommendations": recommendations
        }

    def get_genre_trends(self) -> List[Dict[str, Any]]:
        """
        Extension: Trend Computations.
        Computes the Average Rating and Total Movies per Genre using SPARQL aggregation.
        """
        query = """
            SELECT ?gLabel (COUNT(?m) as ?movieCount) (AVG(?val) as ?avgRating)
            WHERE {
                ?m a <http://example.org/movielens/Movie> .
                ?m <http://example.org/movielens/hasGenre> ?g .
                ?g <http://www.w3.org/2000/01/rdf-schema#label> ?gLabel .
                
                OPTIONAL {
                    # Join with ratings via the Rating object
                    ?r <http://example.org/movielens/ratingOf> ?m .
                    ?r <http://example.org/movielens/ratingValue> ?val .
                }
            }
            GROUP BY ?gLabel
            HAVING (COUNT(?m) > 10)
            ORDER BY DESC(?avgRating)
        """
        
        trends = []
        try:
            results = self.store.query(query)
            if isinstance(results, pyoxigraph.QuerySolutions):
                for row in results:
                    trends.append({
                        "genre": row["gLabel"].value,
                        "count": int(row["movieCount"].value),
                        "avg_rating": float(row["avgRating"].value) if row["avgRating"] else 0.0
                    })
        except Exception as e:
            print(f"Trend Query Error: {e}")
            return []
            
        return trends

movie_service = MovieService()
