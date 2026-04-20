import os
import json
from openai import OpenAI
from pathlib import Path
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


def extraction_service():

    client = OpenAI(
        api_key=settings.OPENROUTER_API_KEY,
        base_url=settings.OPENROUTER_BASE_URL
    )

    with Session() as session:
        pending_documents = session.query(Document).filter_by(status=DocumentStatus.PENDING).all()

        for doc in pending_documents:
            try:
                doc_path = Path(doc.file_path)
                doc_text =Path(doc_path).read_text(encoding="utf-8")

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
                    session.add(extracted_entity)
                stmt = update(Document).where(Document.id == doc.id).values(status = DocumentStatus.COMPLETED)
                session.execute(stmt)
                session.commit()

            except Exception as e:
                session.rollback()
                stmt = update(Document).where(Document.id == doc.id).values(status = DocumentStatus.FAILED)
                session.execute(stmt)
                session.commit()