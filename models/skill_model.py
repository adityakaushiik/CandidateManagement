from datetime import datetime, timezone
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator, ConfigDict
from bson import ObjectId


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


class SkillBase(BaseModel):
    """Base model for Skill"""

    name: str = Field(..., min_length=1, max_length=100)
    category: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=500)

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        if v:
            return v.strip().title()
        return v

    @field_validator("category")
    @classmethod
    def validate_category(cls, v):
        if v:
            return v.strip().title()
        return v


class SkillCreate(SkillBase):
    """Model for creating a skill"""

    pass


class SkillUpdate(BaseModel):
    """Model for updating a skill - all fields optional"""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    category: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=500)

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        if v:
            return v.strip().title()
        return v

    @field_validator("category")
    @classmethod
    def validate_category(cls, v):
        if v:
            return v.strip().title()
        return v


class SkillInDB(SkillBase):
    """Model for skill in database"""

    model_config = ConfigDict(arbitrary_types_allowed=True, populate_by_name=True)

    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SkillResponse(BaseModel):
    """Model for skill response"""

    model_config = ConfigDict(arbitrary_types_allowed=True, populate_by_name=True)

    id: str = Field(alias="_id")
    name: str
    # category: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_mongo(cls, data: dict):
        """Convert MongoDB document to response model"""
        if not data:
            return None
        data["_id"] = str(data["_id"])
        return cls(**data)


class SkillListResponse(BaseModel):
    """Model for paginated skill list"""

    total: int
    page: int
    page_size: int
    skills: List[SkillResponse]
