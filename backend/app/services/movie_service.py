from typing import List, Optional
import re
from app.repositories.movie_repository import MovieRepository
from app.models.movie_models import MovieDTO, TrendDTO, GenreDTO


class MovieService:
    def __init__(self):
        self.repository = MovieRepository()

    def get_stats(self):
        return self.repository.get_stats()

    def search_movies(
        self,
        genre: Optional[str] = None,
        year_min: Optional[int] = None,
        year_max: Optional[int] = None,
        rating_min: Optional[float] = None,
        rating_max: Optional[float] = None,
        sort: str = "title",
        limit: int = 20,
        offset: int = 0,
    ) -> List[MovieDTO]:
        if genre and not self.repository.check_genre_exists(genre):
            raise ValueError(f"Genre '{genre}' is not defined in the Knowledge Graph.")

        # 1. Fetch Candidates (No Limit/Offset here to allow correct filtering)
        raw_results = self.repository.search_movies(
            genre=genre,
            year_min=None,
            year_max=None,
            rating_min=rating_min,
            rating_max=rating_max,
            limit=None,  # Fetch all to filter in memory
            offset=None,
        )

        all_movies = []
        for row in raw_results:
            title = row["title"]["value"] if "title" in row else "Unknown"

            # Extract Year
            year = 0
            match = re.search(r"\((\d{4})\)", title)
            if match:
                year = int(match.group(1))

            # Filter by Year
            if year_min is not None and year < year_min:
                continue
            if year_max is not None and year > year_max:
                continue

            all_movies.append(
                MovieDTO(
                    id=row["mid"]["value"] if "mid" in row else "",
                    title=title,
                    genres=row["genres"]["value"].split("|") if "genres" in row else [],
                    average_rating=(
                        float(row["avgRating"]["value"]) if "avgRating" in row else None
                    ),
                )
            )

        # 3. Sort (In-Memory)
        # Default or "title"
        all_movies.sort(key=lambda m: m.title)

        # 4. Paginate
        start = offset
        end = offset + limit
        return all_movies[start:end]

    def get_movies(self, limit: int, offset: int, sort: str) -> List[MovieDTO]:
        raw_results = self.repository.get_movies(limit, offset, sort)
        movies = []
        for row in raw_results:
            movies.append(
                MovieDTO(
                    id=row["mid"]["value"] if "mid" in row else "",
                    title=row["title"]["value"] if "title" in row else "Unknown",
                    genres=row["genres"]["value"].split("|") if "genres" in row else [],
                    average_rating=(
                        float(row["avgRating"]["value"]) if "avgRating" in row else None
                    ),
                )
            )
        return movies

    def search_movies_by_title(
        self,
        title: str,
        genre: Optional[str] = None,
        year_min: Optional[int] = None,
        year_max: Optional[int] = None,
        rating_min: Optional[float] = None,
        rating_max: Optional[float] = None,
    ) -> List[MovieDTO]:
        if genre and not self.repository.check_genre_exists(genre):
            raise ValueError(f"Genre '{genre}' is not defined in the Knowledge Graph.")

        # Fetch Candidates (No Limit here to allow correct filtering in memory if needed, 
        # but better to do as much as possible in SPARQL now)
        raw_results = self.repository.search_movies_by_title(
            title, genre, year_min, year_max, rating_min, rating_max, limit=None
        )
        
        movies = []
        for row in raw_results:
            row_title = row["title"]["value"] if "title" in row else "Unknown"
            
            # Extract Year (Duplicate logic, ideally refactor)
            year = 0
            match = re.search(r"\((\d{4})\)", row_title)
            if match:
                year = int(match.group(1))

            # Filter by Year (In-Memory fallback if SPARQL didn't catch it or for robust check)
            if year_min is not None and year < year_min:
                continue
            if year_max is not None and year > year_max:
                continue

            movies.append(
                MovieDTO(
                    id=row["mid"]["value"] if "mid" in row else "",
                    title=row_title,
                    genres=row["genres"]["value"].split("|") if "genres" in row else [],
                    average_rating=(
                        float(row["avgRating"]["value"]) if "avgRating" in row else None
                    ),
                )
            )
        
        # Sort by title
        movies.sort(key=lambda m: m.title)
        
        # We enforce a limit here since we removed it from SPARQL to ensure filtering correctness
        # or we could re-add limit to SPARQL if filtering is fully pushed down.
        # For now, let's limit return size to 20 to mimic previous behavior
        return movies[:20]

    def get_trends(self) -> List[TrendDTO]:
        raw_results = self.repository.get_trends()
        trends = []
        for row in raw_results:
            trends.append(
                TrendDTO(
                    genre=row["gLabel"]["value"],
                    movie_count=int(row["movieCount"]["value"]),
                    average_rating=float(row["avgRating"]["value"]),
                )
            )
        return trends

    def compare_movies(self, movie_ids: List[int]):
        # Convert IDs to strings for repository
        ids_str = [str(mid) for mid in movie_ids]
        raw_results = self.repository.get_movies_by_ids(ids_str)

        comparison_data = []
        for row in raw_results:
            title = row["title"]["value"]

            # Extract Year
            year = "Unknown"
            match = re.search(r"\((\d{4})\)", title)
            if match:
                year = match.group(1)

            comparison_data.append(
                {
                    "id": row["mid"]["value"],
                    "title": title,
                    "year": year,
                    "genres": row["genres"]["value"] if "genres" in row else "",
                    "average_rating": (
                        float(row["avgRating"]["value"]) if "avgRating" in row else 0.0
                    ),
                    "review_count": (
                        int(row["reviewCount"]["value"]) if "reviewCount" in row else 0
                    ),
                }
            )

        return comparison_data

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

        return {"nodes": list(nodes.values()), "links": links}

    def get_genres(self):
        raw_data = self.repository.get_genres_hierarchy()
        # Group by SuperCategory for easier frontend consumption
        hierarchy = {}
        uncategorized = []

        for row in raw_data:
            g_label = row["genreLabel"]["value"]
            super_cat = row.get("superCategoryLabel", {}).get("value")

            if super_cat:
                if super_cat not in hierarchy:
                    hierarchy[super_cat] = []
                hierarchy[super_cat].append(g_label)
            else:
                # Avoid duplicates if a genre appears multiple times?
                # Our query lists genres. If a genre has NO super cat, it goes here.
                # However, our super categories themselves are genres (e.g. Emotional).
                # We might want to filter them out from "uncategorized" list if they are keys in hierarchy.
                uncategorized.append(g_label)

        final_uncategorized = [g for g in uncategorized if g not in hierarchy]

        return {"categories": hierarchy, "other": final_uncategorized}

    def create_movie(self, title: str, genres: List[str]):
        return self.repository.create_movie(title, genres)

    def get_movie_by_id(self, movie_id: str):
        return self.repository.get_movie_by_id(movie_id)

    def update_movie(self, movie_id: str, title: str, genres: List[str]):
        return self.repository.update_movie(movie_id, title, genres)

    def delete_movie(self, movie_id: str):
        return self.repository.delete_movie(movie_id)

    def add_rating(self, user_id: str, movie_id: str, value: float):
        return self.repository.add_rating(user_id, movie_id, value)

    def get_facet_data(self):
        return {
            "genres": self.get_genres(),
            "yearRange": self.repository.get_year_range(),
            "ratingRange": self.repository.get_rating_range(),
        }
