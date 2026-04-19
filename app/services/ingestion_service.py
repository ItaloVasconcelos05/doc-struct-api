from pathlib import Path
from app.repositories.database import Session
from app.models.documents import Document, DocumentStatus
from sqlalchemy import select


def ingest_documents(directory: str):

    source_path = Path(directory)
    inserted_count = 0
    skipped_files = 0

    with Session() as session:
        for doc_path in source_path.glob("*.txt"):
            stmt = select(Document).where(Document.file_path == str(doc_path))
            existing_doc = session.execute(stmt).scalars().first()

            if not existing_doc:
                new_doc = Document(
                    filename=doc_path.name,
                    file_path=str(doc_path),
                    status=DocumentStatus.PENDING
                )
                session.add(new_doc)
                print(f"Documento {doc_path.name} inserido.")
                inserted_count += 1

            else:
                print(f"Documento {doc_path.name} já existe.")
                skipped_files += 1

        
        session.commit()

        return (
            {
                "inserted": inserted_count,
                "skipped": skipped_files
            }
        )