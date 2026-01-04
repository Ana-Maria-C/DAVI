# WADe MovieLens Backend

This is the FastAPI backend service for the WADe MovieLens project.
It relies on an embedded RDF store (Oxigraph) loaded with data from `../data/movielens_graph.ttl`.

## Prerequisites

- Python 3.9+
- The RDF data must be generated first (run `../data/convert_csv_to_rdf.py`).

## Installation

```bash
pip install -r requirements.txt
```

## Running the Server

You can start the server using Uvicorn:

```bash
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

The server will start at `http://127.0.0.1:8000`.

## API Documentation

- **Swagger UI**: `http://127.0.0.1:8000/docs`
- **ReDoc**: `http://127.0.0.1:8000/redoc`
