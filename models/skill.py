from typing import Optional

from pydantic import Field

from config.database import Base
from models.common_mixin import CommonMixin


class SkillModel(Base, CommonMixin):
    """Base model for Skill"""

    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
