from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from app.models.documents import DocumentStatus
from uuid import UUID

class EntityBase(BaseModel):
    entity_value: str
    entity_type: str
    confidence: float = Field(ge=0, le=1)

class EntityCreate(EntityBase):
    pass

class EntityResponse(EntityBase):
    id: UUID
    document_id: UUID
    model_config = ConfigDict(from_attributes=True)

class DocumentBase(BaseModel):
    filename: str
    file_path: str
    status: DocumentStatus = DocumentStatus.PENDING 

class DocumentCreate(DocumentBase):
    pass

class DocumentResponse(DocumentBase):
    id: UUID
    creation_time: datetime
    extracted_entities: list[EntityResponse] = []
    model_config = ConfigDict(from_attributes=True)

class IngestResponse(BaseModel):
    inserted: int
    skipped: int
    status: str = "success"

class IngestRequest(BaseModel):
    directory: str