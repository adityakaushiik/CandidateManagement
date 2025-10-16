from datetime import datetime, timezone
from typing import Optional
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ASCENDING, DESCENDING

from models.user_model import UserCreate, UserResponse


class UserRepository:
    """Repository for User operations"""

    def __init__(self, database: AsyncIOMotorDatabase):
        self.collection = database.get_collection("users")

    async def create_indexes(self):
        await self.collection.create_index([("email", ASCENDING)], unique=True)
        await self.collection.create_index([("role_id", ASCENDING)])
        await self.collection.create_index([("created_at", DESCENDING)])

    async def create(self, password_hash: str, user: UserCreate) -> UserResponse:
        user_dict = user.model_dump(exclude={"password"})
        user_dict["password_hash"] = password_hash
        user_dict["created_at"] = datetime.now(timezone.utc)
        user_dict["updated_at"] = datetime.now(timezone.utc)
        result = await self.collection.insert_one(user_dict)
        created = await self.collection.find_one({"_id": result.inserted_id})
        return UserResponse.from_mongo(created)

    async def create_with_id(self, custom_id: str, password_hash: str, user: UserCreate) -> UserResponse:
        """Create a user with a manually provided _id (not exposed via API). Supports string or ObjectId."""
        user_dict = user.model_dump(exclude={"password"})
        user_dict["password_hash"] = password_hash
        user_dict["created_at"] = datetime.now(timezone.utc)
        user_dict["updated_at"] = datetime.now(timezone.utc)
        # Use string id as-is; if a valid ObjectId string is passed, you can convert to ObjectId
        try:
            # If it's a valid ObjectId string, convert; otherwise fallback to string id
            user_dict["_id"] = ObjectId(custom_id) if ObjectId.is_valid(custom_id) else custom_id
        except Exception:
            user_dict["_id"] = custom_id
        await self.collection.insert_one(user_dict)
        created = await self.collection.find_one({"_id": user_dict["_id"]})
        return UserResponse.from_mongo(created)

    async def get_by_email(self, email: str) -> Optional[dict]:
        doc = await self.collection.find_one({"email": email})
        return doc

    async def get_by_id(self, user_id: str) -> Optional[dict]:
        # accept either string _id or ObjectId string
        query_id = ObjectId(user_id) if ObjectId.is_valid(user_id) else user_id
        doc = await self.collection.find_one({"_id": query_id})
        return doc

    async def update_password_hash(self, user_id: str, new_hash: str) -> bool:
        query_id = ObjectId(user_id) if ObjectId.is_valid(user_id) else user_id
        result = await self.collection.update_one(
            {"_id": query_id},
            {"$set": {"password_hash": new_hash, "updated_at": datetime.now(timezone.utc)}},
        )
        return result.modified_count > 0

    async def update(self, user_id: str, update_data: dict) -> Optional[UserResponse]:
        query_id = ObjectId(user_id) if ObjectId.is_valid(user_id) else user_id
        if not update_data:
            doc = await self.get_by_id(user_id)
            return UserResponse.from_mongo(doc) if doc else None
        update_data = {k: v for k, v in update_data.items() if v is not None}
        update_data["updated_at"] = datetime.now(timezone.utc)
        result = await self.collection.find_one_and_update(
            {"_id": query_id}, {"$set": update_data}, return_document=True
        )
        return UserResponse.from_mongo(result) if result else None
