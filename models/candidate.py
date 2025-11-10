from sqlalchemy import Column, String, DateTime, Float, Text, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from config.database import Base
from utils.common_mixin import CommonMixin


class CandidateModel(Base, CommonMixin):
    __tablename__ = "candidates"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    total_experience_years = Column(Float, nullable=False, server_default="0.0")
    preferred_locations = Column(JSONB, nullable=False, server_default="[]")
    date_of_birth = Column(DateTime, nullable=False)

    current_location = Column(String(200), nullable=True)
    salary_expectation = Column(Float, nullable=True)

    address = Column(Text, nullable=True)
    projects = Column(JSONB, nullable=True)
    certifications = Column(JSONB, nullable=True)
    languages = Column(JSONB, nullable=True)
    education = Column(JSONB, nullable=True)
    links = Column(JSONB, nullable=True)

    # Relationships
    user = relationship(
        "UserModel",  # The related model class name to establish relationship with UserModel
        back_populates="candidate",  # Name of the reverse relationship attribute in UserModel that references this CandidateModel
    )
    candidate_skills = relationship(
        "CandidateSkillModel",  # The related model class name to establish relationship with CandidateSkillModel junction table
        back_populates="candidate",  # Name of the reverse relationship attribute in CandidateSkillModel that references this CandidateModel
        cascade="all, delete-orphan",  # Automatically delete all related candidate skills when candidate is deleted, and delete orphaned skills
    )
