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

    def search_movies(self, genre: Optional[str], limit: int, offset: int):
        filter_clause = ""
        if genre:
            # EXTENSION 1 (Enhanced): Intelligent Semantic Filtering with Reasoning
            # We use the transitive property :subCategoryOf* defined in schema.ttl
            # This allows searching for "Exciting" and getting "Action", "Horror", etc.
            filter_clause = f"""
                ?m :hasGenre ?g .
                ?g :subCategoryOf* ?superG .
                ?superG rdfs:label ?gLabel .
                FILTER(REGEX(?gLabel, "{genre}", "i"))
            """

        query = f"""
            PREFIX : <http://example.org/movielens/>
            PREFIX schema: <http://schema.org/>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            
            SELECT ?mid ?title (GROUP_CONCAT(DISTINCT ?finalGLabel; separator="|") as ?genres)
            WHERE {{
                ?m a :Movie ;
                   schema:name ?title .
                OPTIONAL {{ ?m :movieId ?mid }} .
                
                {filter_clause}
                
                OPTIONAL {{ 
                    ?m :hasGenre ?gx . 
                    ?gx rdfs:label ?finalGLabel 
                }}
            }}
            GROUP BY ?mid ?title
            LIMIT {limit}
            OFFSET {offset}
        """
        return self.execute_select(query)

    def get_movies(self, limit: int, offset: int, sort: str = "title"):
        # Validate sort parameter to prevent injection
        allowed_sorts = ["title", "year"]
        if sort not in allowed_sorts:
            sort = "title"

        query = f"""
            PREFIX : <http://example.org/movielens/>
            PREFIX schema: <http://schema.org/>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            
            SELECT ?mid ?title ?year ?director ?poster ?description
            WHERE {{
                ?m a :Movie ;
                   schema:name ?title .
                OPTIONAL {{ ?m :movieId ?mid }}
                OPTIONAL {{ ?m :year ?year }}
                OPTIONAL {{ ?m :director ?d . ?d rdfs:label ?director }}
                OPTIONAL {{ ?m :poster ?poster }}
                OPTIONAL {{ ?m :description ?description }}
            }}
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

            SELECT ?gLabel (COUNT(?m) as ?movieCount) (AVG(?val) as ?avgRating)
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

            SELECT ?s ?sLabel ?p ?o ?oLabel ?sType ?oType
            WHERE {{
                # 1. Select a set of central movies
                {{ SELECT ?s WHERE {{ ?s a :Movie }} LIMIT {limit} }}
                
                {{
                    # Case A: Linked Resources (Genres) - Outgoing
                    ?s ?p ?o .
                    FILTER(ISIRI(?o)) # Ensure it's a resource (Genre, etc.)
                    
                    ?s a ?sType .
                    ?o a ?oType .
                    OPTIONAL {{ ?s schema:name ?sLabel }}
                    OPTIONAL {{ ?o rdfs:label ?oLabel }}
                }}
                UNION
                {{
                    # Case B: Tags (which are Literals in the data)
                    # We convert them to pseudo-nodes for visualization
                    ?s :hasTagLabel ?tagVal .
                    
                    BIND(:hasTagLabel as ?p)
                    # Generate a unique synthetic URI for the tag node
                    BIND(IRI(CONCAT("urn:tag:", ENCODE_FOR_URI(?tagVal))) as ?o)
                    BIND(?tagVal as ?oLabel)
                    BIND(<http://example.org/movielens/Tag> as ?oType)
                    
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

            SELECT ?title (GROUP_CONCAT(?gLabel; separator="|") as ?genres)
            WHERE {{
                {movie_uri} schema:name ?title .
                OPTIONAL {{ 
                    {movie_uri} :hasGenre ?g .
                    ?g rdfs:label ?gLabel .
                }}
            }}
            GROUP BY ?title
        """
        res = self.execute_select(query)
        if not res:
            return None
        return {
            "id": movie_id,
            "title": res[0]["title"]["value"],
            "genres": (
                res[0]["genres"]["value"].split("|") if res[0].get("genres") else []
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
