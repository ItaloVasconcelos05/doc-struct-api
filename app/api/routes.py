from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session as DBSession
from uuid import UUID
from sqlalchemy import select

from app.api.schemas import DocumentResponse, EntityResponse, IngestResponse, IngestRequest
from app.models.documents import Document, ExtractedEntity
from app.repositories.database import get_db
from app.services.ingestion_service import ingest_documents
from app.services.extraction_service import extraction_service

router = APIRouter(prefix="/documents", tags=["documents"])

@router.get("/", response_model=List[DocumentResponse])
def list_documents(db: DBSession = Depends(get_db)):
    stmt = select(Document)
    documents = db.execute(stmt).scalars().all()
    return documents

@router.get("/{id}", response_model=DocumentResponse)
def get_document(id: UUID, db: DBSession = Depends(get_db)):
    document = db.get(Document, id)

    if not document:
        raise HTTPException(status_code=404, detail="Documento não encontrado")
    return document

@router.get("/{id}/entities", response_model=List[EntityResponse])
def get_document_entities(id: UUID, db: DBSession = Depends(get_db)):
    document = db.get(Document, id)

    if not document:
        raise HTTPException(status_code=404, detail="Documento não encontrado")
    return document.extracted_entities  
   
@router.post("/ingest", response_model=IngestResponse)
def ingest(request: IngestRequest,db: DBSession = Depends(get_db)):
    return ingest_documents(request.directory)

@router.post("/process")
def process_documents(db: DBSession = Depends(get_db)):
    return extraction_service()