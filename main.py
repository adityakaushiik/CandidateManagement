from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from routes.resume_route import resume_route
from routes.candidate_route import candidate_route
from routes.skill_route import skill_route
from routes.auth_route import auth_route
from routes.search_route import search_route
from config.database import connect_to_mongo, close_mongo_connection, get_database
from repositories.candidate_repository import CandidateRepository
from repositories.skill_repository import SkillRepository
from repositories.user_repository import UserRepository

app = FastAPI(
    title="Candidate Management API",
    description="API for managing candidates and skills",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    await connect_to_mongo()

    # Optionally create indexes
    db = get_database()
    # _ = CandidateRepository(db)
    # _ = UserRepository(db)
    # _ = SkillRepository(db)
    # await _.create_indexes()


@app.on_event("shutdown")
async def shutdown_event():
    await close_mongo_connection()

# Routers
app.include_router(resume_route, prefix="/api/resume", tags=["Resume"])
app.include_router(candidate_route, prefix="/api/candidates", tags=["Candidates"])
app.include_router(skill_route, prefix="/api/skills", tags=["Skills"])
app.include_router(auth_route, prefix="/api/auth", tags=["Auth"])
app.include_router(search_route, prefix="/api/search", tags=["Search"])
