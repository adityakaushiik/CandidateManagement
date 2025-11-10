from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import FastAPI
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordBearer
from requests import Response
from starlette.middleware.cors import CORSMiddleware

from config.database import db

# Import all models to ensure they are registered with SQLAlchemy
from models import (
    UserModel,
    CandidateModel,
    CandidateSkillModel,
    CompanyModel,
    JobModel,
    JoiningTime,
    SkillModel,
    ScheduleProcessModel,
    UserScheduleModel,
    ExperienceModel,
)
from routes.user_auth_route import user_auth_route

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.init_postgres()
    await db.init_mongo()

    yield

    await db.close()


app = FastAPI(
    title="Candidate Management API",
    description="API for managing candidates and skills",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include your routers here
app.include_router(user_auth_route, tags=["User Authentication"])


@app.get("/auth")
async def auth(token: Annotated[str, Depends(oauth2_scheme)]):
    return {"token": token}
