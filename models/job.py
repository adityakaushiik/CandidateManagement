from enum import Enum
from sqlalchemy import Column, Integer, String, ForeignKey, Enum as SAEnum, Text
from sqlalchemy.orm import relationship

from config.database import Base
from models.common_mixin import CommonMixin


class JoiningTime(Enum):
    IMMEDIATE = "immediate"
    WITH_NOTICE = "with_notice"
    FLEXIBLE = "flexible"
    NEGOTIABLE = "negotiable"


class JobModel(Base, CommonMixin):
    """Postgres-backed Job DB model."""
    __tablename__ = "jobs"

    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    designation = Column(String(200), nullable=False)
    number_of_openings = Column(Integer, nullable=False, default=1)
    joining_time = Column(SAEnum(JoiningTime, name="joining_time_enum"), nullable=True)
    description = Column(Text, nullable=True)

    # Relationships
    company = relationship("CompanyModel", back_populates="jobs")
    user_schedules = relationship("UserScheduleModel", back_populates="job", cascade="all, delete-orphan")

    def __repr__(self) -> str:  # pragma: no cover - simple repr
        return f"<Job id={self.id} designation='{self.designation}' company_id={self.company_id}>"

