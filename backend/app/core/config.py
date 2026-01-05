from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "WADe MovieLens API"
    VERSION: str = "2.0.0"
    API_PREFIX: str = "/api"
    
    FUSEKI_URL: str = "http://localhost:3030"
    DATASET_NAME: str = "movielens"
    
    @property
    def SPARQL_ENDPOINT(self) -> str:
        return f"{self.FUSEKI_URL}/{self.DATASET_NAME}/sparql"
    
    @property
    def UPDATE_ENDPOINT(self) -> str:
        return f"{self.FUSEKI_URL}/{self.DATASET_NAME}/update"

settings = Settings()
