from sqlalchemy import String, Enum, func, ForeignKey, CheckConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from uuid import UUID, uuid4 as UUID4
from enum import Enum as PyEnum
from datetime import datetime

class DocumentStatus(PyEnum):
    FAILED = 'failed'
    PENDING = 'pending'
    PROCESSING = 'processing'
    COMPLETED = 'completed'

class Base(DeclarativeBase):
    pass

class Document(Base):
    __tablename__ = 'documents'
    
    id: Mapped[UUID] = mapped_column(primary_key=True, default=UUID4)
    status: Mapped[DocumentStatus] = mapped_column(Enum(DocumentStatus), default=DocumentStatus.PENDING, nullable=False)
    creation_time: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)
    filename: Mapped[str] = mapped_column(String, nullable=False)
    file_path: Mapped[str] = mapped_column(String, nullable=False)
    extracted_entities: Mapped[list['ExtractedEntity']] = relationship (back_populates='document')
    
class ExtractedEntity(Base):
    __tablename__ = 'extracted_entities'
    __table_args__ = (
        CheckConstraint('confidence >= 0 AND confidence <= 1', name='confidence_range'),
    )
    
    
    id: Mapped[UUID] = mapped_column(primary_key=True, default=UUID4)
    document_id: Mapped[UUID] = mapped_column(ForeignKey('documents.id'), nullable=False)
    entity_type: Mapped[str] = mapped_column(String, nullable=False)
    entity_value: Mapped[str] = mapped_column(String, nullable=False)
    confidence: Mapped[float] = mapped_column(nullable=False)
    document: Mapped["Document"] = relationship(back_populates="extracted_entities")
    