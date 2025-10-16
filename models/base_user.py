from pydantic import BaseModel, EmailStr, Field


class CommonUserBase(BaseModel):
    email: EmailStr
    phone_number: str = Field(..., pattern=r"^\+?[\d\s\-\(\)]{10,20}$")

