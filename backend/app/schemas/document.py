from datetime import datetime

from pydantic import BaseModel, Field


class DocumentRead(BaseModel):
    id: str
    original_filename: str
    content_type: str | None
    file_extension: str
    file_size: int
    status: str
    chunk_count: int
    error_message: str | None
    created_at: datetime
    indexed_at: datetime | None

    model_config = {"from_attributes": True}


class DocumentSearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=2000)
    document_ids: list[str] = Field(default_factory=list)
    top_k: int = Field(default=5, ge=1, le=20)


class RetrievedChunk(BaseModel):
    document_id: str
    chunk_id: str
    chunk_index: int
    text: str
    score: float
    metadata: dict = Field(default_factory=dict)


class DocumentSearchResponse(BaseModel):
    query: str
    results: list[RetrievedChunk]

