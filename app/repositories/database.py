import os
from app.models.documents import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL não definida no arquivo .env")
engine = create_engine(
    DATABASE_URL,
    echo=True,
)

Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)

def create_tables():
    print("Criando tabelas no banco de dados...")
    Base.metadata.create_all(bind=engine)
    print("Tabelas criadas com sucesso!")


