from fastapi import APIRouter, HTTPException, Response
from app.repositories.base_repository import BaseRepository

router = APIRouter(tags=["Linked Data"])

@router.get("/resource/{type}/{id}", summary="Linked Data Resolver")
def get_resource(type: str, id: str):
    """
    Acts as a resolver for custom URIs.
    Example: /resource/Movie/1 -> returns JSON-LD description of Movie 1
    """

    resource_uri = f"http://example.org/movielens/{type}/{id}"


    repo = BaseRepository()
    
    query = f"DESCRIBE <{resource_uri}>"
    
    try:
        repo.sparql.setQuery(query)

        repo.sparql.setReturnFormat("json-ld") 
        
        result = repo.sparql.query().response.read()
        return Response(content=result, media_type="application/ld+json")
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Resource not found or error: {str(e)}")
