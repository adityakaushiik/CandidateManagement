from datetime import datetime, timezone
from typing import Optional, List
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ASCENDING, DESCENDING

from models.candidate_model import CandidateCreate, CandidateUpdate, CandidateResponse


class CandidateRepository:
    """Repository for Candidate CRUD operations"""

    def __init__(self, database: AsyncIOMotorDatabase):
        self.collection = database.get_collection("candidates")

    async def   create_indexes(self):
        """Create indexes for better query performance"""
        await self.collection.create_index([("email", ASCENDING)], unique=True)
        await self.collection.create_index([("phone_number", ASCENDING)])
        await self.collection.create_index([("skills", ASCENDING)])
        await self.collection.create_index([("created_at", DESCENDING)])

    async def create(self, candidate: CandidateCreate) -> CandidateResponse:
        """Create a new candidate"""
        candidate_dict = candidate.model_dump()
        candidate_dict["created_at"] = datetime.now(timezone.utc)
        candidate_dict["updated_at"] = datetime.now(timezone.utc)

        result = await self.collection.insert_one(candidate_dict)
        created_candidate = await self.collection.find_one({"_id": result.inserted_id})
        return CandidateResponse.from_mongo(created_candidate)

    async def get_by_id(self, candidate_id: str) -> Optional[CandidateResponse]:
        """Get candidate by ID"""
        if not ObjectId.is_valid(candidate_id):
            return None

        candidate = await self.collection.find_one({"_id": ObjectId(candidate_id)})
        return CandidateResponse.from_mongo(candidate) if candidate else None

    async def get_by_email(self, email: str) -> Optional[CandidateResponse]:
        """Get candidate by email"""
        candidate = await self.collection.find_one({"email": email})
        return CandidateResponse.from_mongo(candidate) if candidate else None

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 10,
        skill_filter: Optional[str] = None,
        location_filter: Optional[str] = None,
        min_experience: Optional[float] = None,
        sort_by: str = "created_at",
        sort_order: int = -1,
    ) -> tuple[List[CandidateResponse], int]:
        """Get all candidates with pagination and filters"""
        query = {}

        if skill_filter:
            query["skills"] = {"$regex": skill_filter, "$options": "i"}

        if location_filter:
            query["location"] = {"$regex": location_filter, "$options": "i"}

        if min_experience is not None:
            query["total_experience"] = {"$gte": min_experience}

        total = await self.collection.count_documents(query)

        cursor = (
            self.collection.find(query)
            .sort(sort_by, sort_order)
            .skip(skip)
            .limit(limit)
        )
        candidates = []
        async for document in cursor:
            candidates.append(CandidateResponse.from_mongo(document))

        return candidates, total

    async def update(
        self, candidate_id: str, candidate: CandidateUpdate
    ) -> Optional[CandidateResponse]:
        """Update a candidate"""
        if not ObjectId.is_valid(candidate_id):
            return None

        update_data = {
            k: v
            for k, v in candidate.model_dump(exclude_unset=True).items()
            if v is not None
        }

        if not update_data:
            return await self.get_by_id(candidate_id)

        update_data["updated_at"] = datetime.now(timezone.utc)

        result = await self.collection.find_one_and_update(
            {"_id": ObjectId(candidate_id)}, {"$set": update_data}, return_document=True
        )

        return CandidateResponse.from_mongo(result) if result else None

    async def delete(self, candidate_id: str) -> bool:
        """Delete a candidate"""
        if not ObjectId.is_valid(candidate_id):
            return False

        result = await self.collection.delete_one({"_id": ObjectId(candidate_id)})
        return result.deleted_count > 0

    async def search_by_skills(
        self, skills: List[str], match_all: bool = False
    ) -> List[CandidateResponse]:
        """Search candidates by skills"""
        if match_all:
            # Match candidates who have ALL the specified skills
            query = {"skills": {"$all": skills}}
        else:
            # Match candidates who have ANY of the specified skills
            query = {"skills": {"$in": skills}}

        cursor = self.collection.find(query)
        candidates = []
        async for document in cursor:
            candidates.append(CandidateResponse.from_mongo(document))

        return candidates

    async def add_skill_to_candidate(
        self, candidate_id: str, skill: str
    ) -> Optional[CandidateResponse]:
        """Add a skill to candidate"""
        if not ObjectId.is_valid(candidate_id):
            return None

        result = await self.collection.find_one_and_update(
            {"_id": ObjectId(candidate_id)},
            {
                "$addToSet": {"skills": skill.strip().title()},
                "$set": {"updated_at": datetime.now(timezone.utc)},
            },
            return_document=True,
        )

        return CandidateResponse.from_mongo(result) if result else None

    async def remove_skill_from_candidate(
        self, candidate_id: str, skill: str
    ) -> Optional[CandidateResponse]:
        """Remove a skill from candidate"""
        if not ObjectId.is_valid(candidate_id):
            return None

        result = await self.collection.find_one_and_update(
            {"_id": ObjectId(candidate_id)},
            {
                "$pull": {"skills": skill.strip().title()},
                "$set": {"updated_at": datetime.now(timezone.utc)},
            },
            return_document=True,
        )

        return CandidateResponse.from_mongo(result) if result else None
