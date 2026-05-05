import json
from sqlalchemy.orm import Session as DBSession
from openai import OpenAI
from pathlib import Path
from pypdf import PdfReader
from app.repositories.database import Session
from app.models.documents import Document, DocumentStatus, ExtractedEntity
from app.config import settings
from sqlalchemy import update

prompt = """
Atue como um motor de extração de dados (NER) de alta precisão. 
Sua tarefa é analisar o texto enviado pelo usuário e extrair exclusivamente as entidades permitidas.

LISTA DE ENTIDADES PERMITIDAS:
[CNPJ, CPF, DATA, VALOR_MONETARIO, NOME_PESSOA, NOME_ORGANIZACAO, ENDERECO]

REGRAS ESTRITAS:
1. Retorne APENAS o objeto JSON. Proibido incluir saudações, explicações ou texto extra.
2. Formate Datas para o padrão ISO 8601 (AAAA-MM-DD).
3. Formate VALOR_MONETARIO para decimal puro (ex: 1250.50), removendo símbolos de moeda.
4. Se uma entidade não for encontrada com clareza, não a invente.
5. O campo 'confidence' deve refletir a probabilidade matemática P(E|T) de a extração estar correta, em uma escala de 0.0 a 1.0.

FORMATO DE SAÍDA:
{
"entities": [
    {
    "entity_type": "TIPO_DA_ENTIDADE",
    "entity_value": "VALOR_EXTRAÍDO",
    "confidence": 0.95
    }
]
}
"""
def extract_text(file_path: Path) -> str:
    if file_path.suffix == ".txt":
        return file_path.read_text(encoding="utf-8")
    
    elif file_path.suffix == ".pdf":
        reader = PdfReader(file_path)
        extracted_pages = []

        for num_page, page in enumerate(reader.pages):
            text = page.extract_text()

            if text:
                extracted_pages.append(text)

        if not extracted_pages:
            raise ValueError(f"Nenhum texto extraível encontrado em {file_path.name}")
        return "\n\n".join(extracted_pages)
    
def extraction_service(db: DBSession):

    client = OpenAI(
        api_key=settings.OPENROUTER_API_KEY,
        base_url=settings.OPENROUTER_BASE_URL
    )


    pending_documents = db.query(Document).filter_by(status=DocumentStatus.PENDING).all()
    processed_count = 0
    failed_count = 0

    for doc in pending_documents:
        try:
            doc_path = Path(doc.file_path)
            doc_text = extract_text(doc_path)

            response = client.chat.completions.create(
                model = settings.LLM_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": prompt
                    },
                    {
                        "role": "user", 
                        "content": f"TEXTO PARA ANÁLISE:\n\n{doc_text}"},
                ],
                response_format={"type": "json_object"}
            )

            raw_content = response.choices[0].message.content

            data = json.loads(raw_content)
            entities = data.get("entities", [])

            for ent in entities:

                extracted_entity = ExtractedEntity(
                    document_id = doc.id,
                    entity_type = ent["entity_type"],
                    entity_value = ent["entity_value"],
                    confidence = ent["confidence"]
                )
                db.add(extracted_entity)
            stmt = update(Document).where(Document.id == doc.id).values(status = DocumentStatus.COMPLETED)
            db.execute(stmt)
            db.commit()

            processed_count += 1
        except Exception as e:
            db.rollback()
            stmt = update(Document).where(Document.id == doc.id).values(status = DocumentStatus.FAILED)
            db.execute(stmt)
            db.commit()

            failed_count += 1

    return {
        "message": "Processamento de extração finalizado",
        "processed": processed_count,
        "failed": failed_count
    }