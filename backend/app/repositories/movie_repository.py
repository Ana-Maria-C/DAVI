from typing import List, Optional, Dict
from app.repositories.base_repository import BaseRepository


class MovieRepository(BaseRepository):

    def check_genre_exists(self, genre_label: str) -> bool:
        query = f"""
            PREFIX : <http://example.org/movielens/>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            
            ASK {{
                ?g a :Genre ;
                   rdfs:label ?label .
                FILTER(REGEX(?label, "^{genre_label}$", "i"))
            }}
        """
        return self.execute_ask(query)

    def search_movies(
        self,
        genre: Optional[str] = None,
        year_min: Optional[int] = None,
        year_max: Optional[int] = None,
        rating_min: Optional[float] = None,
        rating_max: Optional[float] = None,
        limit: Optional[int] = 20,
        offset: Optional[int] = 0,
    ):
        filters = []

        if genre:
            # EXTENSION 1 (Enhanced): Intelligent Semantic Filtering with Reasoning
            filters.append(
                f"""
                ?m :hasGenre ?g .
                ?g :subCategoryOf* ?superG .
                ?superG rdfs:label ?gLabel .
                FILTER(REGEX(?gLabel, "{genre}", "i"))
            """
            )

        # Removed SPARQL Year filtering as requested to use In-Memory extraction
        # if year_min is not None:
        #     filters.append(f"?m :year ?year . FILTER(xsd:integer(?year) >= {year_min})")
        # if year_max is not None:
        #     filters.append(f"?m :year ?year . FILTER(xsd:integer(?year) <= {year_max})")

        if rating_min is not None or rating_max is not None:
            pass

        filter_clause = "\n".join(filters)

        limit_clause = f"LIMIT {limit}" if limit is not None else ""
        offset_clause = f"OFFSET {offset}" if offset is not None else ""

        # Basic query structure
        query = f"""
            PREFIX : <http://example.org/movielens/>
            PREFIX schema: <http://schema.org/>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
            
            SELECT ?mid ?title (GROUP_CONCAT(DISTINCT ?finalGLabel; separator="|") as ?genres) (AVG(?rVal) as ?avgRating)
            WHERE {{
                ?m a :Movie ;
                   schema:name ?title .
                OPTIONAL {{ ?m :movieId ?mid }} .
                
                {filter_clause}
                
                OPTIONAL {{ 
                    ?m :year ?year .
                }}

                OPTIONAL {{ 
                    ?m :hasGenre ?gx . 
                    ?gx rdfs:label ?finalGLabel 
                }}
                
                OPTIONAL {{
                    ?r :ratingOf ?m ;
                        :ratingValue ?rVal .
                }}
            }}
            GROUP BY ?mid ?title
            {limit_clause}
            {offset_clause}
        """
        # If rating filter is needed, wrap in subquery or use HAVING
        if rating_min is not None or rating_max is not None:
            min_r = rating_min if rating_min is not None else 0
            max_r = rating_max if rating_max is not None else 5

            query = f"""
                PREFIX : <http://example.org/movielens/>
                PREFIX schema: <http://schema.org/>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
                
                SELECT ?mid ?title (GROUP_CONCAT(DISTINCT ?finalGLabel; separator="|") as ?genres) (AVG(?rVal) as ?avgRating)
                WHERE {{
                    ?m a :Movie ;
                       schema:name ?title .
                    OPTIONAL {{ ?m :movieId ?mid }} .
                    
                    {filter_clause}
                    
                    # Rating Filter
                    ?r :ratingOf ?m ;
                       :ratingValue ?rVal .
                    
                    OPTIONAL {{ 
                        ?m :hasGenre ?gx . 
                        ?gx rdfs:label ?finalGLabel 
                    }}
                }}
                GROUP BY ?mid ?title
                HAVING (AVG(?rVal) >= {min_r} && AVG(?rVal) <= {max_r})
                {limit_clause}
                {offset_clause}
            """

        return self.execute_select(query)

    def get_movies(self, limit: int, offset: int, sort: str = "title"):
        # Validate sort parameter to prevent injection
        allowed_sorts = ["title"]
        if sort not in allowed_sorts:
            sort = "title"

        query = f"""
            PREFIX : <http://example.org/movielens/>
            PREFIX schema: <http://schema.org/>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            
            SELECT ?mid ?title ?director ?poster ?description (AVG(?rVal) as ?avgRating) (GROUP_CONCAT(DISTINCT ?genreLabel; separator="|") as ?genres)
            WHERE {{
                ?m a :Movie ;
                   schema:name ?title .
                OPTIONAL {{ ?m :movieId ?mid }}
                OPTIONAL {{ ?m :director ?d . ?d rdfs:label ?director }}
                OPTIONAL {{ ?m :poster ?poster }}
                OPTIONAL {{ ?m :description ?description }}
                OPTIONAL {{
                    ?r :ratingOf ?m ;
                       :ratingValue ?rVal .
                }}
                OPTIONAL {{
                    ?m :hasGenre ?g .
                    ?g rdfs:label ?genreLabel .
                }}
            }}
            GROUP BY ?mid ?title ?director ?poster ?description
            ORDER BY ?{sort}
            LIMIT {limit}
            OFFSET {offset}
        """
        return self.execute_select(query)

    def get_stats(self):
        query = """
            PREFIX : <http://example.org/movielens/>
            SELECT 
                (COUNT(?m) as ?movies)
                (COUNT(?u) as ?users)
                (COUNT(?g) as ?genres)
                (COUNT(?r) as ?ratings)
            WHERE {
                { ?m a :Movie } UNION
                { ?u a :User } UNION
                { ?g a :Genre } UNION
                { ?r a :Rating }
            }
        """

        def count_class(cls_uri):
            q = f"SELECT (COUNT(?s) as ?c) WHERE {{ ?s a <{cls_uri}> }}"
            res = self.execute_select(q)
            return int(res[0]["c"]["value"]) if res else 0

        return {
            "movies": count_class("http://example.org/movielens/Movie"),
            "users": count_class("http://example.org/movielens/User"),
            "genres": count_class("http://example.org/movielens/Genre"),
            "ratings": count_class("http://example.org/movielens/Rating"),
        }

    def get_trends(self):
        query = """
            PREFIX : <http://example.org/movielens/>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

            SELECT ?gLabel (COUNT(DISTINCT ?m) as ?movieCount) (AVG(?val) as ?avgRating)
            WHERE {
                ?m a :Movie ;
                   :hasGenre ?g .
                ?g rdfs:label ?gLabel .
                
                OPTIONAL {
                    ?r :ratingOf ?m ;
                       :ratingValue ?val .
                }
            }
            GROUP BY ?gLabel
            HAVING (COUNT(?m) > 10)
            ORDER BY DESC(?avgRating)
        """
        return self.execute_select(query)

    def get_most_reviewed_movies(self, limit=10):
        query = f"""
            PREFIX : <http://example.org/movielens/>
            PREFIX schema: <http://schema.org/>
            
            SELECT ?mid ?title (COUNT(?r) as ?reviewCount) (AVG(?val) as ?avgRating)
            WHERE {{
                ?m a :Movie ;
                   schema:name ?title ;
                   :movieId ?mid .
                
                ?r :ratingOf ?m ;
                   :ratingValue ?val .
            }}
            GROUP BY ?mid ?title
            ORDER BY DESC(?reviewCount)
            LIMIT {limit}
        """
        return self.execute_select(query)

    def get_highest_rated_movies(self, limit=10, min_reviews=20):
        query = f"""
            PREFIX : <http://example.org/movielens/>
            PREFIX schema: <http://schema.org/>
            
            SELECT ?mid ?title (AVG(?val) as ?avgRating) (COUNT(?r) as ?reviewCount)
            WHERE {{
                ?m a :Movie ;
                   schema:name ?title ;
                   :movieId ?mid .
                
                ?r :ratingOf ?m ;
                   :ratingValue ?val .
            }}
            GROUP BY ?mid ?title
            HAVING (COUNT(?r) >= {min_reviews})
            ORDER BY DESC(?avgRating)
            LIMIT {limit}
        """
        return self.execute_select(query)

    def get_yearly_trends_data(self, year: int):
        # Top Reviewed in Year
        famous_query = f"""
            PREFIX : <http://example.org/movielens/>
            PREFIX schema: <http://schema.org/>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
            
            SELECT ?mid ?title (COUNT(?r) as ?reviewCount) (AVG(?val) as ?avgRating)
            WHERE {{
                ?m a :Movie ;
                   schema:name ?title ;
                   :movieId ?mid ;
                # Filter by extracting year from title "(YYYY)"
                FILTER(REGEX(?title, "\\\\({year}\\\\)", "i"))
                
                ?r :ratingOf ?m ;
                   :ratingValue ?val .
            }}
            GROUP BY ?mid ?title
            ORDER BY DESC(?reviewCount)
            LIMIT 10
        """

        # Best Rated in Year (min 5 reviews to be significant for a single year slice)
        rated_query = f"""
            PREFIX : <http://example.org/movielens/>
            PREFIX schema: <http://schema.org/>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
            
            SELECT ?mid ?title (AVG(?val) as ?avgRating) (COUNT(?r) as ?reviewCount)
            WHERE {{
                ?m a :Movie ;
                   schema:name ?title ;
                   :movieId ?mid ;
                # Filter by extracting year from title
                FILTER(REGEX(?title, "\\\\({year}\\\\)", "i"))
                
                ?r :ratingOf ?m ;
                   :ratingValue ?val .
            }}
            GROUP BY ?mid ?title
            HAVING (COUNT(?r) >= 5) 
            ORDER BY DESC(?avgRating)
            LIMIT 10
        """

        return {
            "famous": self.execute_select(famous_query),
            "rated": self.execute_select(rated_query),
        }

    def compare_movies(self, movie_id_1: str, movie_id_2: str):
        """
        Finds common attributes between two movies (Genres, Tags, potentially Users who rated both).
        """
        query = f"""
            PREFIX : <http://example.org/movielens/>
            PREFIX schema: <http://schema.org/>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            
            SELECT ?property ?value
            WHERE {{
                # Find common properties
                ?m1 :movieId {movie_id_1} ;
                    ?p ?o .
                ?m2 :movieId {movie_id_2} ;
                    ?p ?o .
                
                # Filter relevant properties
                FILTER(?p IN (:hasGenre, :hasTagLabel))
                
                BIND(STR(?p) AS ?property)
                BIND(STR(?o) AS ?value)
            }}
        """
        return self.execute_select(query)

    def get_graph_data(self, limit=30):
        """
        Returns triples for graph visualization (Nodes + Links).
        Enriched to include Movies, Genres, and connected Tags.
        Optimized to handle Tags as Literals by generating pseudo-URIs.
        """
        query = f"""
            PREFIX : <http://example.org/movielens/>
            PREFIX schema: <http://schema.org/>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

             SELECT ?s ?sLabel ?p ?o ?oLabel ?sType ?oType
            WHERE {{
                # 1. Select Top 50 Most Popular Movies (by rating count)
                {{ 
                    SELECT ?s 
                    WHERE {{ 
                        ?s a :Movie .
                        ?r :ratingOf ?s .
                    }} 
                    GROUP BY ?s 
                    ORDER BY DESC(COUNT(?r)) 
                    LIMIT {limit} 
                }}
                
                {{
                    # Case A: Linked Resources (Genres) - Outgoing
                    ?s ?p ?o .
                    FILTER(ISIRI(?o)) 
                    
                    ?s a ?sType .
                    ?o a ?oType .
                    OPTIONAL {{ ?s schema:name ?sLabel }}
                    OPTIONAL {{ ?o rdfs:label ?oLabel }}
                }}
                UNION
                {{
                    # Case B: Tags
                    ?s :hasTagLabel ?tagVal .
                    BIND(:hasTagLabel as ?p)
                    BIND(IRI(CONCAT("urn:tag:", ENCODE_FOR_URI(?tagVal))) as ?o)
                    BIND(?tagVal as ?oLabel)
                    BIND(<http://example.org/movielens/Tag> as ?oType)
                    
                    ?s a ?sType .
                    OPTIONAL {{ ?s schema:name ?sLabel }}
                }}
                UNION
                {{
                    # Case C: Average Rating Node
                    # Calculate average rating for the movie and link to a "Rating Node"
                    {{
                        SELECT ?s (AVG(?val) as ?avgVal)
                        WHERE {{
                            ?s a :Movie .
                            ?r :ratingOf ?s ;
                               :ratingValue ?val .
                        }}
                        GROUP BY ?s
                    }}
                    BIND(:hasRatingValue as ?p)
                    # Create a rating bucket/node (e.g., "4.5")
                    BIND(xsd:string(ROUND(?avgVal * 2) / 2) as ?ratingStr) 
                    BIND(IRI(CONCAT("urn:rating:", ?ratingStr)) as ?o)
                    BIND(CONCAT("Rating: ", ?ratingStr) as ?oLabel)
                    BIND(<http://example.org/movielens/RatingGroup> as ?oType)

                    ?s a ?sType .
                    OPTIONAL {{ ?s schema:name ?sLabel }}
                }}
            }}
        """
        return self.execute_select(query)

    def get_genres_hierarchy(self):
        """
        Returns all genres and their super-categories (if any).
        Useful for building a 'Smart Filter' dropdown on Frontend.
        """
        query = """
            PREFIX : <http://example.org/movielens/>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

            SELECT ?genre ?genreLabel ?superCategory ?superCategoryLabel
            WHERE {
                ?genre a :Genre ;
                       rdfs:label ?genreLabel .
                
                OPTIONAL {
                    ?genre :subCategoryOf ?superCategory .
                    ?superCategory rdfs:label ?superCategoryLabel .
                }
            }
            ORDER BY ?superCategoryLabel ?genreLabel
        """
        return self.execute_select(query)

    def get_max_movie_id(self) -> int:
        query = """
            PREFIX : <http://example.org/movielens/>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
            SELECT (MAX(?idVal) as ?maxId)
            WHERE {
                ?m a :Movie ;
                   :movieId ?id .
                BIND(xsd:integer(?id) as ?idVal)
            }
        """
        res = self.execute_select(query)
        try:
            return int(res[0]["maxId"]["value"])
        except:
            return 0

    def get_year_range(self):
        query = """
            PREFIX : <http://example.org/movielens/>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
            SELECT (MIN(?y) as ?minYear) (MAX(?y) as ?maxYear)
            WHERE {
                ?m a :Movie ;
                   :year ?year .
                BIND(xsd:integer(?year) as ?y)
            }
        """
        res = self.execute_select(query)
        if res and "minYear" in res[0] and "maxYear" in res[0]:
            try:
                return {
                    "min": int(res[0]["minYear"]["value"]),
                    "max": int(res[0]["maxYear"]["value"]),
                }
            except:
                return {"min": 1900, "max": 2025}
        return {"min": 1900, "max": 2025}

    def get_rating_range(self):
        query = """
            PREFIX : <http://example.org/movielens/>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
            SELECT (MIN(?v) as ?minRating) (MAX(?v) as ?maxRating)
            WHERE {
                ?r a :Rating ;
                   :ratingValue ?val .
                BIND(xsd:float(?val) as ?v)
            }
        """
        res = self.execute_select(query)
        if res and "minRating" in res[0] and "maxRating" in res[0]:
            try:
                return {
                    "min": float(res[0]["minRating"]["value"]),
                    "max": float(res[0]["maxRating"]["value"]),
                }
            except:
                return {"min": 0, "max": 5}
        return {"min": 0, "max": 5}

    def create_movie(self, title: str, genres: List[str]):
        new_id = self.get_max_movie_id() + 1
        movie_uri = f"<http://example.org/movielens/Movie/{new_id}>"

        genre_triples = ""
        for g in genres:
            genre_triples += (
                f"    :hasGenre <http://example.org/movielens/Genre/{g}> ;\n"
            )

        query = f"""
            PREFIX : <http://example.org/movielens/>
            PREFIX schema: <http://schema.org/>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
            PREFIX prov: <http://www.w3.org/ns/prov#>
            
            INSERT DATA {{
                {movie_uri} a :Movie ;
                    :movieId "{new_id}" ;
                    schema:name "{title}" ;
                    {genre_triples}
                    prov:wasDerivedFrom :MovieLensDataset .
            }}
        """
        self.execute_update(query)
        return new_id

    def get_movie_by_id(self, movie_id: str):
        movie_uri = f"<http://example.org/movielens/Movie/{movie_id}>"
        query = f"""
            PREFIX : <http://example.org/movielens/>
            PREFIX schema: <http://schema.org/>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

            SELECT ?title 
                   (AVG(?rVal) as ?avgRating) 
                   (COUNT(?r) as ?reviewCount) 
                   (GROUP_CONCAT(DISTINCT ?gLabel; separator="|") as ?genres)
                   (GROUP_CONCAT(DISTINCT ?tagVal; separator="|") as ?tags)
            WHERE {{
                {movie_uri} schema:name ?title .
                
                OPTIONAL {{ 
                    {movie_uri} :hasGenre ?g .
                    ?g rdfs:label ?gLabel .
                }}
                
                OPTIONAL {{
                    ?r :ratingOf {movie_uri} ;
                       :ratingValue ?rVal .
                }}
                
                OPTIONAL {{
                    {movie_uri} :hasTagLabel ?tagVal .
                }}
            }}
            GROUP BY ?title
        """
        res = self.execute_select(query)
        if not res:
            return None

        row = res[0]
        return {
            "id": movie_id,
            "title": row["title"]["value"],
            "genres": (
                row["genres"]["value"].split("|")
                if row.get("genres") and row["genres"]["value"]
                else []
            ),
            "tags": (
                row["tags"]["value"].split("|")
                if row.get("tags") and row["tags"]["value"]
                else []
            ),
            "average_rating": (
                float(row["avgRating"]["value"]) if "avgRating" in row else 0.0
            ),
            "review_count": (
                int(row["reviewCount"]["value"]) if "reviewCount" in row else 0
            ),
        }

    def update_movie(self, movie_id: str, title: str, genres: List[str]):
        movie_uri = f"<http://example.org/movielens/Movie/{movie_id}>"

        genre_triples = ""
        for g in genres:
            genre_triples += (
                f"    :hasGenre <http://example.org/movielens/Genre/{g}> ;\n"
            )

        query = f"""
            PREFIX : <http://example.org/movielens/>
            PREFIX schema: <http://schema.org/>
            
            DELETE {{
                {movie_uri} schema:name ?oldTitle .
                {movie_uri} :hasGenre ?oldGenre .
            }}
            INSERT {{
                {movie_uri} schema:name "{title}" .
                {movie_uri} {genre_triples.strip()[:-1] if genre_triples else ""} .
            }}
            WHERE {{
                OPTIONAL {{ {movie_uri} schema:name ?oldTitle }}
                OPTIONAL {{ {movie_uri} :hasGenre ?oldGenre }}
            }}
        """
        self.execute_update(query)
        return True

    def delete_movie(self, movie_id: str):
        movie_uri = f"<http://example.org/movielens/Movie/{movie_id}>"

        query = f"""
            PREFIX : <http://example.org/movielens/>
            
            DELETE {{
                ?m ?p ?o .
                ?r ?rp ?ro .
            }}
            WHERE {{
                BIND({movie_uri} as ?m)
                
                # 1. Movie triples
                ?m ?p ?o .
                
                # 2. Related Ratings
                OPTIONAL {{
                    ?r :ratingOf ?m .
                    ?r ?rp ?ro .
                }}
            }}
        """
        return self.execute_update(query)

    def add_rating(self, user_id: str, movie_id: str, rating_val: float):
        rating_id = f"{user_id}_{movie_id}"
        rating_uri = f"<http://example.org/movielens/Rating/{rating_id}>"
        user_uri = f"<http://example.org/movielens/User/{user_id}>"
        movie_uri = f"<http://example.org/movielens/Movie/{movie_id}>"

        query = f"""
            PREFIX : <http://example.org/movielens/>
            PREFIX schema: <http://schema.org/>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
            
            INSERT DATA {{
                 {rating_uri} a :Rating ;
                     :ratedBy {user_uri} ;
                     :ratingOf {movie_uri} ;
                     :ratingValue "{rating_val}"^^xsd:float .
            }}
        """
        return self.execute_update(query)

    def get_movies_by_ids(self, movie_ids: List[str]):
        if not movie_ids:
            return []

        # VALUES clause construction with URIs
        uris_str = " ".join(
            [f"<http://example.org/movielens/Movie/{mid}>" for mid in movie_ids]
        )

        query = f"""
            PREFIX : <http://example.org/movielens/>
            PREFIX schema: <http://schema.org/>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            
            SELECT ?mid ?title (AVG(?rVal) as ?avgRating) (COUNT(?r) as ?reviewCount) (GROUP_CONCAT(DISTINCT ?genreName; separator=", ") as ?genres)
            WHERE {{
                VALUES ?m {{ {uris_str} }}
                
                ?m a :Movie ;
                   schema:name ?title .
                
                OPTIONAL {{ 
                    ?m :hasGenre ?g .
                    ?g rdfs:label ?genreName .
                }}

                OPTIONAL {{ ?m :movieId ?mid }}
                
                OPTIONAL {{
                    ?r :ratingOf ?m ;
                       :ratingValue ?rVal .
                }}
            }}
            GROUP BY ?mid ?title
        """
        return self.execute_select(query)
