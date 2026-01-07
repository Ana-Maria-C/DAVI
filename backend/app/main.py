from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routes import movies, sparql, resources, analysis

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_PREFIX}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(movies.router, prefix=settings.API_PREFIX)
app.include_router(
    sparql.router, prefix=settings.API_PREFIX
)  # Now it will be /api/sparql
app.include_router(
    analysis.router, prefix=f"{settings.API_PREFIX}/analysis"
)  # /api/v1/analysis
app.include_router(resources.router, prefix="")  # Root /resource/...


@app.on_event("startup")
def startup_msg():
    print(f"Starting {settings.PROJECT_NAME}...")
    print(f"Connecting to Fuseki at: {settings.FUSEKI_URL}")


@app.get("/")
def home():
    return {"status": "running", "service": settings.PROJECT_NAME}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
