from fastapi import FastAPI

from app.api.health_api import router as health_router
from app.api.query_api import router as query_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Governed Biomedical GraphRAG",
        description="Governed biomedical GraphRAG pipeline with evidence contracts.",
        version="0.1.0",
    )

    app.include_router(health_router)
    app.include_router(query_router)

    return app


app = create_app()
