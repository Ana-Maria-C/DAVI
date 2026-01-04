from fastapi import APIRouter, Request, Response, HTTPException, Body
from typing import Optional
from pydantic import BaseModel, Field
from services.sparql_service import sparql_service

router = APIRouter(
    tags=["SPARQL"]
)

class SparqlQuery(BaseModel):
    query: str = Field(..., example="SELECT * WHERE { ?s ?p ?o } LIMIT 5", description="The SPARQL query to execute.")

@router.post("/sparql", summary="Execute a SPARQL Query (POST)", description="Execute a SPARQL query sent in the request body.")
async def sparql_endpoint_post(
    request: Request,
    body: Optional[SparqlQuery] = None
):
    """
    Accepts SPARQL queries via POST.
    Supports:
    1. Parsing `application/json` with a "query" field.
    2. Parsing `application/x-www-form-urlencoded` form data.
    3. Parsing raw `application/sparql-query` body.
    """
    query: Optional[str] = None
    content_type = request.headers.get("content-type", "")
    
    # 1. Handle JSON Body (Swagger default)
    if body and body.query:
        query = body.query
    
    # 2. Handle Raw Body (Standard SPARQL Protocol)
    if not query:
        raw_body = await request.body()
        if "application/sparql-query" in content_type:
            query = raw_body.decode("utf-8")
        elif "application/x-www-form-urlencoded" in content_type:
             form = await request.form()
             query = form.get("query")
    
    if not query:
        # Fallback if body was plain string?
        if body and isinstance(body, str):
             query = body

    if not query:
        raise HTTPException(status_code=400, detail="Missing SPARQL query in body.")

    try:
        return sparql_service.execute_query(query)
    except Exception as e:
        return Response(content=str(e), status_code=400)

@router.get("/sparql", summary="Execute a SPARQL Query (GET)", description="Execute a SPARQL query via query parameter.")
def sparql_endpoint_get(query: str):
    """
    Standard SPARQL 1.1 GET Endpoint.
    """
    if not query:
        raise HTTPException(status_code=400, detail="Missing query parameter")
    try:
        return sparql_service.execute_query(query)
    except Exception as e:
        return Response(content=str(e), status_code=400)
