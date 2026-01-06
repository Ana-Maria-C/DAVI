from fastapi import APIRouter, HTTPException, Request, Response
from app.repositories.base_repository import BaseRepository

router = APIRouter(tags=["SPARQL"])

from pydantic import BaseModel, Field
from typing import Optional


class SparqlQueryBody(BaseModel):
    query: str = Field(
        ...,
        description="The SPARQL query to execute",
        example="SELECT * WHERE { ?s ?p ?o } LIMIT 5",
    )


@router.get("/sparql", summary="Execute SPARQL Query (GET)")
def execute_sparql_get(query: str):
    """
    Executes a SPARQL query via GET parameter.
    """
    if not query:
        raise HTTPException(status_code=400, detail="Missing query parameter")
    return _run_query(query)


@router.post("/sparql", summary="Execute SPARQL Query (POST)")
async def execute_sparql_post(request: Request, body: Optional[SparqlQueryBody] = None):
    """
    Executes a SPARQL query via POST used for larger queries.
    Supports JSON body, Form data, or Raw SPARQL string.
    """
    content_type = request.headers.get("content-type", "")
    query = None

    if body and body.query:
        query = body.query

    if not query:
        if "application/x-www-form-urlencoded" in content_type:
            form = await request.form()
            query = form.get("query")
        elif "application/sparql-query" in content_type:
            raw = await request.body()
            query = raw.decode("utf-8")

    if not query:
        raise HTTPException(status_code=400, detail="Missing query in body")

    return _run_query(query)


def _run_query(query: str):
    repo = BaseRepository()
    try:
        repo.sparql.setQuery(query)
        # Return properly formatted JSON
        return repo.sparql.query().convert()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
