from sqlalchemy import Column, String, Text
from sqlalchemy.orm import relationship

from config.database import Base
from utils.common_mixin import CommonMixin


class SkillModel(Base, CommonMixin):
    """Base model for Skill"""

    __tablename__ = "skills"

    name = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)

    # Relationships
    candidate_skills = relationship(
        "CandidateSkillModel",  # The related model class name to establish relationship with CandidateSkillModel junction table
        back_populates="skill",  # Name of the reverse relationship attribute in CandidateSkillModel that references this SkillModel
    )
