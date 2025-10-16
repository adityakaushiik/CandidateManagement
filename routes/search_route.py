from typing import Optional
from fastapi import APIRouter, Depends, Query, Request, HTTPException, status

from config.jwt_utils import require_auth
from services.fuzzy_search import FuzzySearchService
from dependencies.repository_deps import get_fuzzy_search_service
from models.search_model import UserSearchResponse, CandidateSearchResponse
from models.user_model import UserResponse
from models.candidate_model import CandidateResponse
from utils.common_constants import UserRoles

search_route = APIRouter()


@search_route.get("/users", response_model=UserSearchResponse)
@require_auth(roles=[UserRoles.ADMIN, UserRoles.SUB_ADMIN])
async def search_users(
    request: Request,
    q: str = Query(..., description="Search query (searches first_name, last_name, email, phone_number)", min_length=1),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    role_id: Optional[int] = Query(None, description="Filter by role ID"),
    fuzzy_service: FuzzySearchService = Depends(get_fuzzy_search_service)
):
    """
    Fuzzy search for users by first_name, last_name, email, or phone_number.
    Supports partial matches and typo tolerance.
    Only accessible to admins and sub-admins.
    """
    try:
        # Build additional filters if role_id is provided
        filters = {"role_id": role_id} if role_id else None

        if filters:
            results, total = await fuzzy_service.search_advanced(
                collection_name="users",
                search_term=q,
                filters=filters,
                page=page,
                page_size=page_size
            )
        else:
            results, total = await fuzzy_service.search(
                collection_name="users",
                search_term=q,
                page=page,
                page_size=page_size
            )

        # Convert to UserResponse objects
        user_responses = [UserResponse.from_mongo(doc) for doc in results]

        return UserSearchResponse(
            total=total,
            page=page,
            page_size=page_size,
            results=user_responses
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error performing search: {str(e)}"
        )


@search_route.get("/candidates", response_model=CandidateSearchResponse)
@require_auth(roles=[UserRoles.ADMIN, UserRoles.SUB_ADMIN])
async def search_candidates(
    request: Request,
    q: str = Query(..., description="Search query (searches first_name, last_name, email, phone_number)", min_length=1),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    location: Optional[str] = Query(None, description="Filter by location"),
    min_experience: Optional[float] = Query(None, ge=0, description="Minimum years of experience"),
    fuzzy_service: FuzzySearchService = Depends(get_fuzzy_search_service)
):
    """
    Fuzzy search for candidates by first_name, last_name, email, or phone_number.
    Supports partial matches and typo tolerance.
    Only accessible to admins and sub-admins.
    """
    try:
        # Build additional filters
        filters = {}
        if location:
            filters["location"] = {"$regex": location, "$options": "i"}
        if min_experience is not None:
            filters["total_experience"] = {"$gte": min_experience}

        if filters:
            results, total = await fuzzy_service.search_advanced(
                collection_name="candidates",
                search_term=q,
                filters=filters,
                page=page,
                page_size=page_size
            )
        else:
            results, total = await fuzzy_service.search(
                collection_name="candidates",
                search_term=q,
                page=page,
                page_size=page_size
            )

        # Convert to CandidateResponse objects
        candidate_responses = [CandidateResponse.from_mongo(doc) for doc in results]

        return CandidateSearchResponse(
            total=total,
            page=page,
            page_size=page_size,
            results=candidate_responses
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error performing search: {str(e)}"
        )

