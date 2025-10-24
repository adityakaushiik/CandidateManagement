from sqlalchemy import Column, Integer, ForeignKey, String, Float
from sqlalchemy.orm import relationship

from config.database import Base
from utils.common_mixin import CommonMixin


class CandidateSkill(Base, CommonMixin):
    """Junction table linking candidates with their skills, including proficiency details."""
    __tablename__ = "candidate_skills"

    # Foreign Keys
    candidate_id = Column(Integer, ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False, index=True)
    skill_id = Column(Integer, ForeignKey("skills.id", ondelete="CASCADE"), nullable=False, index=True)

    # Additional attributes for the relationship
    proficiency_level = Column(
        String(50),
        nullable=True
    )  # e.g., "Beginner", "Intermediate", "Advanced", "Expert"

    years_of_experience = Column(
        Float,
        nullable=True
    )  # Number of years of experience with this skill

    # Relationships
    candidate = relationship(
        "CandidateBase",  # The related model class name to establish relationship with CandidateBase
        back_populates="candidate_skills"  # Name of the reverse relationship attribute in CandidateBase that references this junction table
    )
    skill = relationship(
        "SkillModel",  # The related model class name to establish relationship with SkillModel
        back_populates="candidate_skills"  # Name of the reverse relationship attribute in SkillModel that references this junction table
    )

    def __repr__(self) -> str:  # pragma: no cover - trivial
        return f"<CandidateSkill candidate_id={self.candidate_id} skill_id={self.skill_id} proficiency='{self.proficiency_level}'>"

