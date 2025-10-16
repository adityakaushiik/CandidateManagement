from datetime import datetime, timezone
from typing import Optional, List
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ASCENDING, DESCENDING

from models.skill_model import SkillCreate, SkillUpdate, SkillResponse


class SkillRepository:
    """Repository for Skill CRUD operations"""

    def __init__(self, database: AsyncIOMotorDatabase):
        self.collection = database.get_collection("skills")

    async def create_indexes(self):
        """Create indexes for better query performance"""
        await self.collection.create_index([("name", ASCENDING)], unique=True)
        await self.collection.create_index([("category", ASCENDING)])
        await self.collection.create_index([("created_at", DESCENDING)])

    async def create(self, skill: SkillCreate) -> SkillResponse:
        """Create a new skill"""
        skill_dict = skill.model_dump()
        skill_dict["created_at"] = datetime.now(timezone.utc)
        skill_dict["updated_at"] = datetime.now(timezone.utc)

        result = await self.collection.insert_one(skill_dict)
        created_skill = await self.collection.find_one({"_id": result.inserted_id})
        return SkillResponse.from_mongo(created_skill)

    async def get_by_id(self, skill_id: str) -> Optional[SkillResponse]:
        """Get skill by ID"""
        if not ObjectId.is_valid(skill_id):
            return None

        skill = await self.collection.find_one({"_id": ObjectId(skill_id)})
        return SkillResponse.from_mongo(skill) if skill else None

    async def get_by_name(self, name: str) -> Optional[SkillResponse]:
        """Get skill by name"""
        skill = await self.collection.find_one({"name": name.strip().title()})
        return SkillResponse.from_mongo(skill) if skill else None

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 10,
        category_filter: Optional[str] = None,
        search: Optional[str] = None,
        sort_by: str = "name",
        sort_order: int = 1,
    ) -> tuple[List[SkillResponse], int]:
        """Get all skills with pagination and filters"""
        query = {}

        if category_filter:
            query["category"] = {"$regex": category_filter, "$options": "i"}

        if search:
            query["name"] = {"$regex": search, "$options": "i"}

        total = await self.collection.count_documents(query)

        cursor = (
            self.collection.find(query)
            .sort(sort_by, sort_order)
            .skip(skip)
            .limit(limit)
        )
        skills = []
        async for document in cursor:
            skills.append(SkillResponse.from_mongo(document))

        return skills, total

    async def get_all_names(self) -> List[str]:
        """Get all skill names"""
        cursor = self.collection.find({}, {"name": 1})
        skills = []
        async for document in cursor:
            skills.append(document["name"])
        return sorted(skills)

    async def get_by_category(self, category: str) -> List[SkillResponse]:
        """Get all skills in a category"""
        cursor = self.collection.find(
            {"category": {"$regex": category, "$options": "i"}}
        )
        skills = []
        async for document in cursor:
            skills.append(SkillResponse.from_mongo(document))
        return skills

    async def update(
        self, skill_id: str, skill: SkillUpdate
    ) -> Optional[SkillResponse]:
        """Update a skill"""
        if not ObjectId.is_valid(skill_id):
            return None

        update_data = {
            k: v
            for k, v in skill.model_dump(exclude_unset=True).items()
            if v is not None
        }

        if not update_data:
            return await self.get_by_id(skill_id)

        update_data["updated_at"] = datetime.now(timezone.utc)

        result = await self.collection.find_one_and_update(
            {"_id": ObjectId(skill_id)}, {"$set": update_data}, return_document=True
        )

        return SkillResponse.from_mongo(result) if result else None

    async def delete(self, skill_id: str) -> bool:
        """Delete a skill"""
        if not ObjectId.is_valid(skill_id):
            return False

        result = await self.collection.delete_one({"_id": ObjectId(skill_id)})
        return result.deleted_count > 0

    async def bulk_create(self, skills: List[SkillCreate]) -> List[SkillResponse]:
        """Bulk create skills"""
        skill_dicts = []
        for skill in skills:
            skill_dict = skill.model_dump()
            skill_dict["created_at"] = datetime.now(timezone.utc)
            skill_dict["updated_at"] = datetime.now(timezone.utc)
            skill_dicts.append(skill_dict)

        result = await self.collection.insert_many(skill_dicts)
        created_skills = []
        for inserted_id in result.inserted_ids:
            skill = await self.collection.find_one({"_id": inserted_id})
            created_skills.append(SkillResponse.from_mongo(skill))

        return created_skills


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

    async def create_indexes(self):
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
                "$set": {"updated_at": datetime.utcnow()},
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
                "$set": {"updated_at": datetime.utcnow()},
            },
            return_document=True,
        )

        return CandidateResponse.from_mongo(result) if result else None
