from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from config.database import get_database
from repositories.candidate_repository import CandidateRepository
from repositories.skill_repository import SkillRepository
from repositories.user_repository import UserRepository
from services.fuzzy_search import FuzzySearchService
from config.jwt_utils import verify_jwt

security = HTTPBearer()


def get_candidate_repository(database=Depends(get_database)) -> CandidateRepository:
    """Dependency to get candidate repository"""
    return CandidateRepository(database)


def get_skill_repository(database=Depends(get_database)) -> SkillRepository:
    """Dependency to get skill repository"""
    return SkillRepository(database)


def get_user_repository(database=Depends(get_database)) -> UserRepository:
    """Dependency to get user repository"""
    return UserRepository(database)


def get_fuzzy_search_service(database=Depends(get_database)) -> FuzzySearchService:
    """Dependency to get fuzzy search service"""
    return FuzzySearchService(database)


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Get the current authenticated user from JWT token"""
    try:
        token = credentials.credentials
        payload = verify_jwt(token)
        return payload
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
