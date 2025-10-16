from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from bson import ObjectId

from models.base_user import CommonUserBase


class PyObjectId(ObjectId):
    """Custom ObjectId type for Pydantic"""

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, info=None):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema, handler):
        return {"type": "string"}


class UserBase(CommonUserBase):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    # role_id aligns with utils.common_constants.UserRoles values (int)
    role_id: int = Field(..., description="Role ID from UserRoles enum")


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=128)


class UserInDB(UserBase):
    model_config = ConfigDict(arbitrary_types_allowed=True, populate_by_name=True)
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    password_hash: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class UserResponse(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, populate_by_name=True)
    id: str = Field(alias="_id")
    first_name: str
    last_name: str
    email: str
    phone_number: Optional[str] = None
    role_id: int
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_mongo(cls, data: dict):
        if not data:
            return None
        data = data.copy()
        data["_id"] = str(data["_id"])
        # remove password hash if present
        data.pop("password_hash", None)
        return cls(**data)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
