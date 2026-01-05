# WADe MovieLens Backend

This is the backend service for the WADe MovieLens project, built with **FastAPI** and **Apache Jena Fuseki**.
It follows a **Service-Oriented Architecture (SOA)** with a Repository Pattern.

## Prerequisites

*   **Python 3.9+**
*   **Docker & Docker Compose** (for the Knowledge Graph Store)

## Installation

1.  **Clone the repository**:
    ```bash
    git clone <repository_url>
    cd DAVI/backend
    ```

2.  **Create a Virtual Environment**:
    ```bash
    python -m venv .venv
    # Windows
    .venv\Scripts\activate
    # Linux/Mac
    source .venv/bin/activate
    ```

3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## Infrastructure Setup (Fuseki)

The project uses **Apache Jena Fuseki** as an external SPARQL endpoint.

1.  **Start Fuseki**:
    Navigate to the project root (where `docker-compose.yml` is located) and run:
    ```bash
    docker-compose up -d
    ```
    *This starts Fuseki at `http://localhost:3030`.*

2.  **Initialize & Load Data**:
    We have a script that creates the dataset and uploads the `movielens_graph.ttl` file.
    *(Make sure you are in the project root)*
    ```bash
    python data/upload_to_fuseki.py
    ```

## Running the Application

To start the FastAPI backend (Development Mode):

```bash
# From the 'backend' directory
python -m uvicorn app.main:app --reload
```

The server will start at `http://127.0.0.1:8000`.

## API Documentation

*   **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
*   **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

## Project Structure

```text
backend/
├── app/
│   ├── api/
│   │   └── routes/       # API Controllers (Movies, SPARQL)
│   ├── core/             # Configuration (Fuseki URL)
│   ├── models/           # Pydantic Models (DTOs)
│   ├── repositories/     # SPARQL Query Logic (Fuseki interactions)
│   ├── services/         # Business Logic
│   └── main.py           # Application Entry Point
└── requirements.txt
```
