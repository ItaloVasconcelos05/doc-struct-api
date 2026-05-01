from fastapi import FastAPI
from app.api.routes import router
from app.repositories.database import create_tables
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Iniciando aplicação...")
    create_tables()
    yield
    print("Finalizando aplicação...")

app = FastAPI(lifespan=lifespan)
app.include_router(router)