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
            # EXTENSION 1: Intelligent Semantic Filtering
            # Use 'rdfs:subClassOf*' if Genres were a hierarchy (e.g. Action -> Superhero).
            filter_clause = f"""
                ?m :hasGenre ?g .
                ?g rdfs:label ?gLabel .
                FILTER(REGEX(?gLabel, "{genre}", "i"))
            """

        query = f"""
            PREFIX : <http://example.org/movielens/>
            PREFIX schema: <http://schema.org/>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            
            SELECT ?mid ?title (GROUP_CONCAT(?gLabel; separator="|") as ?genres)
            WHERE {{
                ?m a :Movie ;
                   schema:name ?title .
                OPTIONAL {{ ?m :movieId ?mid }} .
                
                {filter_clause}
                
                OPTIONAL {{ 
                    ?m :hasGenre ?gx . 
                    ?gx rdfs:label ?gLabel 
                }}
            }}
            GROUP BY ?mid ?title
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
            "ratings": count_class("http://example.org/movielens/Rating")
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

    def get_graph_data(self, limit=50):
        """
        Returns triples constructed specifically for graph visualization (Nodes + Links).
        """
        query = f"""
            PREFIX : <http://example.org/movielens/>
            PREFIX schema: <http://schema.org/>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

            SELECT ?s ?sLabel ?p ?o ?oLabel ?sType ?oType
            WHERE {{
                {{
                    SELECT ?s WHERE {{ ?s a :Movie }} LIMIT {limit}
                }}
                ?s ?p ?o .
                ?s a ?sType .
                OPTIONAL {{ ?s schema:name ?sLabel }}
                
                # Only include links to Genres or other internal resources, not literals usually
                FILTER(ISIRI(?o)) 
                ?o a ?oType .
                OPTIONAL {{ ?o rdfs:label ?oLabel }}
            }}
        """
        return self.execute_select(query)
