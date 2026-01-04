from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from services.rdf_store import rdf_store

from controllers.movie_controller import router as movie_router
from controllers.sparql_controller import router as sparql_router

app = FastAPI(
    title="MovieLens RDF Service", 
    version="1.0.0",
    description="Backend for the WADe MovieLens Project, providing SPARQL access and intelligent endpoints."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(movie_router)
app.include_router(sparql_router)

@app.on_event("startup")
def startup_event():
    """Initializes the RDF store on startup."""
    rdf_store.load_data()

@app.get("/")
def home():
    print("DEBUG: Accessing / route")
    
    return {
        "service": "WADe MovieLens Backend",
        "status": "running",
        "docs": "/docs"
    }

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
