from typing import List
from pydantic import BaseModel
from models.user_model import UserResponse
from models.candidate_model import CandidateResponse


class FuzzySearchRequest(BaseModel):
    """Request model for fuzzy search"""
    search_term: str
    page: int = 1
    page_size: int = 20
    min_score: float = 0.0


class UserSearchResponse(BaseModel):
    """Response model for user fuzzy search results"""
    total: int
    page: int
    page_size: int
    results: List[UserResponse]


class CandidateSearchResponse(BaseModel):
    """Response model for candidate fuzzy search results"""
    total: int
    page: int
    page_size: int
    results: List[CandidateResponse]
