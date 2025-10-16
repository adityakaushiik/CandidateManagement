from datetime import datetime, timezone
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
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


class LinksModel(BaseModel):
    """Model for professional links"""

    linkedin: Optional[str] = None
    github: Optional[str] = None
    portfolio: Optional[str] = None
    other: Optional[List[str]] = None

    @field_validator("linkedin", "github", "portfolio")
    @classmethod
    def validate_url(cls, v):
        if v and not v.startswith(("http://", "https://")):
            return f"https://{v}"
        return v


class CandidateBase(CommonUserBase):
    """Base model for Candidate"""

    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    date_of_birth: Optional[datetime] = None
    location: Optional[str] = Field(None, max_length=200)
    skills: Optional[List[str]] = Field(default_factory=list)
    degree: Optional[str] = Field(None, max_length=200)
    total_experience: Optional[float] = Field(None, ge=0, le=50)
    links: Optional[LinksModel] = None

    @field_validator("skills")
    @classmethod
    def validate_skills(cls, v):
        if v:
            return [skill.strip() for skill in v if skill.strip()]
        return []

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_names(cls, v):
        if v:
            return v.strip().title()
        return v


class CandidateCreate(CandidateBase):
    """Model for creating a candidate"""

    pass


class CandidateUpdate(BaseModel):
    """Model for updating a candidate - all fields optional"""

    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    date_of_birth: Optional[datetime] = None
    phone_number: Optional[str] = Field(None, pattern=r"^\+?[\d\s\-\(\)]{10,20}$")
    location: Optional[str] = Field(None, max_length=200)
    email: Optional[EmailStr] = None
    skills: Optional[List[str]] = None
    degree: Optional[str] = Field(None, max_length=200)
    total_experience: Optional[float] = Field(None, ge=0, le=50)
    links: Optional[LinksModel] = None

    @field_validator("skills")
    @classmethod
    def validate_skills(cls, v):
        if v:
            return [skill.strip() for skill in v if skill.strip()]
        return v

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_names(cls, v):
        if v:
            return v.strip().title()
        return v


class CandidateInDB(CandidateBase):
    """Model for candidate in database"""

    model_config = ConfigDict(arbitrary_types_allowed=True, populate_by_name=True)

    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CandidateResponse(BaseModel):
    """Model for candidate response"""

    model_config = ConfigDict(arbitrary_types_allowed=True, populate_by_name=True)

    id: str = Field(alias="_id")
    first_name: str
    last_name: str
    date_of_birth: Optional[datetime] = None
    phone_number: str
    location: Optional[str] = None
    email: str
    skills: Optional[List[str]] = None
    degree: Optional[str] = None
    total_experience: Optional[float] = None
    links: Optional[LinksModel] = None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_mongo(cls, data: dict):
        """Convert MongoDB document to response model"""
        if not data:
            return None
        data["_id"] = str(data["_id"])
        return cls(**data)


class CandidateListResponse(BaseModel):
    """Model for paginated candidate list"""

    total: int
    page: int
    page_size: int
    candidates: List[CandidateResponse]
