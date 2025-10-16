from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from config.jwt_utils import require_auth
from models.candidate_model import (
    CandidateCreate,
    CandidateUpdate,
    CandidateResponse,
    CandidateListResponse,
)
from repositories.candidate_repository import CandidateRepository
from dependencies.repository_deps import get_candidate_repository
from utils.common_constants import UserRoles

candidate_route = APIRouter()


@candidate_route.post(
    "/", response_model=CandidateResponse, status_code=status.HTTP_201_CREATED
)
async def create_candidate(
    candidate: CandidateCreate,
    repo: CandidateRepository = Depends(get_candidate_repository),
):
    """Create a new candidate"""
    # Check if email already exists
    existing = await repo.get_by_email(str(candidate.email))
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Candidate with this email already exists",
        )

    try:
        return await repo.create(candidate)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating candidate: {str(e)}",
        )


@candidate_route.get("/", response_model=CandidateListResponse)
@require_auth(roles=[UserRoles.ADMIN,UserRoles.SUB_ADMIN])
async def get_all_candidates(
    request: Request,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    skill: Optional[str] = Query(None, description="Filter by skill"),
    location: Optional[str] = Query(None, description="Filter by location"),
    min_experience: Optional[float] = Query(
        None, ge=0, description="Minimum years of experience"
    ),
    sort_by: str = Query("created_at", description="Field to sort by"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order"),
    repo: CandidateRepository = Depends(get_candidate_repository),
):
    """Get all candidates with pagination and filters"""
    skip = (page - 1) * page_size
    sort_direction = -1 if sort_order == "desc" else 1

    candidates, total = await repo.get_all(
        skip=skip,
        limit=page_size,
        skill_filter=skill,
        location_filter=location,
        min_experience=min_experience,
        sort_by=sort_by,
        sort_order=sort_direction,
    )

    return CandidateListResponse(
        total=total, page=page, page_size=page_size, candidates=candidates
    )


@candidate_route.get("/{candidate_id}", response_model=CandidateResponse)
@require_auth(roles=[UserRoles.ADMIN,UserRoles.SUB_ADMIN])
async def get_candidate(
    request: Request,
    candidate_id: str, repo: CandidateRepository = Depends(get_candidate_repository)
):
    """Get a candidate by ID"""
    candidate = await repo.get_by_id(candidate_id)
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Candidate not found"
        )
    return candidate


@candidate_route.put("/{candidate_id}", response_model=CandidateResponse)
async def update_candidate(
    candidate_id: str,
    candidate_update: CandidateUpdate,
    repo: CandidateRepository = Depends(get_candidate_repository),
):
    """Update a candidate"""
    # Check if candidate exists
    existing = await repo.get_by_id(candidate_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Candidate not found"
        )

    # If email is being updated, check if new email already exists
    if candidate_update.email and candidate_update.email != existing.email:
        email_exists = await repo.get_by_email(str(candidate_update.email))
        if email_exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists"
            )

    updated = await repo.update(candidate_id, candidate_update)
    return updated


@candidate_route.delete("/{candidate_id}", status_code=status.HTTP_204_NO_CONTENT)
@require_auth(roles=[UserRoles.ADMIN,UserRoles.SUB_ADMIN])
async def delete_candidate(
    request: Request,
    candidate_id: str, repo: CandidateRepository = Depends(get_candidate_repository)
):
    """Delete a candidate"""
    deleted = await repo.delete(candidate_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Candidate not found"
        )


@candidate_route.post(
    "/{candidate_id}/skills/{skill_name}", response_model=CandidateResponse
)
async def add_skill_to_candidate(
    candidate_id: str,
    skill_name: str,
    repo: CandidateRepository = Depends(get_candidate_repository),
):
    """Add a skill to a candidate"""
    candidate = await repo.add_skill_to_candidate(candidate_id, skill_name)
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Candidate not found"
        )
    return candidate


@candidate_route.delete(
    "/{candidate_id}/skills/{skill_name}", response_model=CandidateResponse
)
async def remove_skill_from_candidate(
    candidate_id: str,
    skill_name: str,
    repo: CandidateRepository = Depends(get_candidate_repository),
):
    """Remove a skill from a candidate"""
    candidate = await repo.remove_skill_from_candidate(candidate_id, skill_name)
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Candidate not found"
        )
    return candidate


@candidate_route.post("/search/by-skills", response_model=List[CandidateResponse])
@require_auth(roles=[UserRoles.ADMIN,UserRoles.SUB_ADMIN])
async def search_candidates_by_skills(
    request: Request,
    skills: List[str],
    match_all: bool = Query(
        False, description="If true, matches candidates with ALL skills"
    ),
    repo: CandidateRepository = Depends(get_candidate_repository),
):
    """Search candidates by skills"""
    return await repo.search_by_skills(skills, match_all)
