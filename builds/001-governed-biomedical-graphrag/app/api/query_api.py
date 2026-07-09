from fastapi import APIRouter
from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1)


class QueryResponse(BaseModel):
    message: str
    query: str


router = APIRouter(tags=["query"])


@router.post("/query", response_model=QueryResponse)
def query_placeholder(request: QueryRequest) -> QueryResponse:
    return QueryResponse(
        message="Query pipeline placeholder. Full governed GraphRAG pipeline will be added later.",
        query=request.query,
    )
