from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from config.database import get_db


@asynccontextmanager
async def lifespan():

    db = get_db()
    await db.init_postgres()
    await db.init_mongo()

    yield

    await db.close()



app = FastAPI(
    title="Candidate Management API",
    description="API for managing candidates and skills",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)