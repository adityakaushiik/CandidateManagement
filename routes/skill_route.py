from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from config.jwt_utils import require_auth
from models.skill_model import (
    SkillCreate,
    SkillUpdate,
    SkillResponse,
    SkillListResponse,
)
from repositories.skill_repository import SkillRepository
from dependencies.repository_deps import get_skill_repository
from utils.common_constants import UserRoles

skill_route = APIRouter()


@skill_route.post(
    "/", response_model=SkillResponse, status_code=status.HTTP_201_CREATED
)
@require_auth(roles=[UserRoles.ADMIN,UserRoles.SUB_ADMIN])
async def create_skill(
    request: Request,
    skill: SkillCreate, repo: SkillRepository = Depends(get_skill_repository)
):
    """Create a new skill"""
    # Check if skill name already exists
    existing = await repo.get_by_name(skill.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Skill with this name already exists",
        )

    try:
        return await repo.create(skill)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating skill: {str(e)}",
        )


@skill_route.post(
    "/bulk", response_model=List[SkillResponse], status_code=status.HTTP_201_CREATED
)
async def bulk_create_skills(
    skills: List[SkillCreate], repo: SkillRepository = Depends(get_skill_repository)
):
    """Bulk create skills"""
    try:
        return await repo.bulk_create(skills)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating skills: {str(e)}",
        )


@skill_route.get("/", response_model=SkillListResponse)
@require_auth(roles=[UserRoles.ADMIN,UserRoles.SUB_ADMIN])
async def get_all_skills(
    request: Request,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search by skill name"),
    sort_by: str = Query("name", description="Field to sort by"),
    sort_order: str = Query("asc", regex="^(asc|desc)$", description="Sort order"),
    repo: SkillRepository = Depends(get_skill_repository),
):
    """Get all skills with pagination and filters"""
    skip = (page - 1) * page_size
    sort_direction = -1 if sort_order == "desc" else 1

    skills, total = await repo.get_all(
        skip=skip,
        limit=page_size,
        category_filter=category,
        search=search,
        sort_by=sort_by,
        sort_order=sort_direction,
    )

    return SkillListResponse(total=total, page=page, page_size=page_size, skills=skills)


@skill_route.get("/names", response_model=List[str])
@require_auth(roles=[UserRoles.ADMIN,UserRoles.SUB_ADMIN])
async def get_all_skill_names(
    request: Request,
    repo: SkillRepository = Depends(get_skill_repository)
):
    """Get all skill names (useful for autocomplete)"""
    return await repo.get_all_names()


# @skill_route.get("/category/{category}", response_model=List[SkillResponse])
# @require_auth(roles=[UserRoles.ADMIN,UserRoles.SUB_ADMIN])
# async def get_skills_by_category(
#     request: Request,
#     category: str, repo: SkillRepository = Depends(get_skill_repository)
# ):
#     """Get all skills in a specific category"""
#     return await repo.get_by_category(category)


@skill_route.get("/{skill_id}", response_model=SkillResponse)
@require_auth(roles=[UserRoles.ADMIN,UserRoles.SUB_ADMIN])
async def get_skill(
    request: Request,
    skill_id: str, repo: SkillRepository = Depends(get_skill_repository)
):
    """Get a skill by ID"""
    skill = await repo.get_by_id(skill_id)
    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Skill not found"
        )
    return skill


@skill_route.put("/{skill_id}", response_model=SkillResponse)
@require_auth(roles=[UserRoles.ADMIN,UserRoles.SUB_ADMIN])
async def update_skill(
    request: Request,
    skill_id: str,
    skill_update: SkillUpdate,
    repo: SkillRepository = Depends(get_skill_repository),
):
    """Update a skill"""
    # Check if skill exists
    existing = await repo.get_by_id(skill_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Skill not found"
        )

    # If name is being updated, check if new name already exists
    if skill_update.name and skill_update.name != existing.name:
        name_exists = await repo.get_by_name(skill_update.name)
        if name_exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Skill name already exists",
            )

    updated = await repo.update(skill_id, skill_update)
    return updated


@skill_route.delete("/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
@require_auth(roles=[UserRoles.ADMIN,UserRoles.SUB_ADMIN])
async def delete_skill(
    request: Request,
    skill_id: str, repo: SkillRepository = Depends(get_skill_repository)
):
    """Delete a skill"""
    deleted = await repo.delete(skill_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Skill not found"
        )
