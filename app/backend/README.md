# Influencer Matching Platform - Backend

This is the backend service for the Influencer Matching Platform, built with FastAPI and Docker.

## Project Structure

```
.
├── Dockerfile                  # Instructions to build the Docker image
├── docker-compose.yml          # Docker Compose configuration for the `back` service
├── requirements.txt            # Python dependencies
├── app/                        # Main application folder
│   ├── main.py                 # FastAPI application entrypoint
│   ├── core/                   # Configuration and core settings
│   │   └── config.py
│   ├── api/                    # API routers and endpoints
│   │   ├── api.py              # Main router tying endpoints together
│   │   └── endpoints/
│   │       └── influencers.py  # CRUD endpoints for influencers
│   └── schemas/                # Pydantic schemas (Data Models)
│       ├── influencer.py       # Influencer schemas
│       └── brand.py            # Brand schemas
```

## How to Build and Run locally with Docker

1. Ensure you have [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/) installed.
2. From the root directory (where `docker-compose.yml` is located), run the following command:
   ```bash
   docker-compose up --build
   ```
3. The backend container will spin up, and the API will be available at `http://localhost:8000`. Hot-reloading is enabled via the configured volume mounts.

## Accessing API Documentation

FastAPI automatically generates interactive OpenAPI documentation (Swagger). Once the container is running, you can access it visually via your browser:

* **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
* **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

## API Assumptions and Pending Dependencies

* **In-Memory State:** Currently, the application uses an in-memory Python list as a transient database to power the CRUD endpoints. Restarting the server or container will reset the data back to its initial mock state.
* **Database Integration:** There is a pending dependency to integrate a persistent database (e.g., PostgreSQL). This will replace the in-memory array and provide robust data modeling with an ORM like SQLAlchemy in future iterations.
* **Authentication & Authorization:** Authentication is completely bypassed for the MVP to speed up initial integration testing. Securing the endpoints (via OAuth2 / JWT tokens) is a pending milestone.
