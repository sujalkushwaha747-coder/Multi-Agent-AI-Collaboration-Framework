from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import db_session, document_service
from app.schemas.document import (
    DocumentRead,
    DocumentSearchRequest,
    DocumentSearchResponse,
    RetrievedChunk,
)
from app.services.document_service import DocumentService

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload", response_model=DocumentRead, status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(db_session),
    service: DocumentService = Depends(document_service),
):
    return await service.upload(db, file)


@router.get("", response_model=list[DocumentRead])
def list_documents(
    db: Session = Depends(db_session),
    service: DocumentService = Depends(document_service),
):
    return service.list_documents(db)


@router.post("/{document_id}/index", response_model=DocumentRead)
def index_document(
    document_id: str,
    db: Session = Depends(db_session),
    service: DocumentService = Depends(document_service),
):
    return service.index(db, document_id)


@router.delete("/{document_id}", status_code=204)
def delete_document(
    document_id: str,
    db: Session = Depends(db_session),
    service: DocumentService = Depends(document_service),
):
    service.delete(db, document_id)
    return None


@router.post("/search", response_model=DocumentSearchResponse)
def search_documents(
    payload: DocumentSearchRequest,
    service: DocumentService = Depends(document_service),
):
    results = service.retrieval.search(
        payload.query,
        document_ids=payload.document_ids,
        top_k=payload.top_k,
    )
    return DocumentSearchResponse(
        query=payload.query,
        results=[
            RetrievedChunk(
                document_id=item.document_id,
                chunk_id=item.chunk_id,
                chunk_index=item.chunk_index,
                text=item.text,
                score=item.score,
                metadata=item.metadata,
            )
            for item in results
        ],
    )

