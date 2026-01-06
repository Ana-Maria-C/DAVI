from SPARQLWrapper import SPARQLWrapper, JSON
from app.core.config import settings

class BaseRepository:
    def __init__(self):
        self.sparql = SPARQLWrapper(settings.SPARQL_ENDPOINT)
        self.sparql.setReturnFormat(JSON)

    def execute_select(self, query: str):
        """Executes a SELECT query and returns the bindings."""
        self.sparql.setQuery(query)
        try:
            results = self.sparql.query().convert()
            return results["results"]["bindings"]
        except Exception as e:
            print(f"SPARQL Error: {e}")
            raise e

    def execute_ask(self, query: str) -> bool:
        """Executes an ASK query and returns the boolean result."""
        self.sparql.setQuery(query)
        try:
            results = self.sparql.query().convert()
            return results["boolean"]
        except Exception as e:
            return False

    def execute_update(self, query: str):
        """Executes an UPDATE query (INSERT, DELETE)."""

        update_sparql = SPARQLWrapper(settings.UPDATE_ENDPOINT)
        update_sparql.setQuery(query)
        update_sparql.setMethod("POST")
        
        update_sparql.setCredentials("admin", "admin")
        
        try:
            update_sparql.query()
            return True
        except Exception as e:
            print(f"SPARQL Update Error: {e}")
            raise e
