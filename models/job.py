from enum import Enum
from sqlalchemy import Column, Integer, String, ForeignKey, Enum as SAEnum, Text
from sqlalchemy.orm import relationship

from config.database import Base
from utils.common_mixin import CommonMixin


class JoiningTime(Enum):
    IMMEDIATE = "immediate"
    WITH_NOTICE = "with_notice"
    FLEXIBLE = "flexible"
    NEGOTIABLE = "negotiable"


class JobModel(Base, CommonMixin):
    """Postgres-backed Job DB model."""

    __tablename__ = "jobs"

    company_id = Column(
        Integer,
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    designation = Column(String(200), nullable=False)
    number_of_openings = Column(Integer, nullable=False, default=1)
    joining_time = Column(SAEnum(JoiningTime, name="joining_time_enum"), nullable=True)
    description = Column(Text, nullable=True)

    # Relationships
    company = relationship(
        "CompanyModel",  # The related model class name to establish relationship with CompanyModel
        back_populates="jobs",  # Name of the reverse relationship attribute in CompanyModel that references this JobModel
    )
    user_schedules = relationship(
        "UserScheduleModel",  # The related model class name to establish relationship with UserScheduleModel
        back_populates="job",  # Name of the reverse relationship attribute in UserScheduleModel that references this JobModel
        cascade="all, delete-orphan",  # Automatically delete all related user schedules when job is deleted, and delete orphaned schedules
    )

    def __repr__(self) -> str:  # pragma: no cover - simple repr
        return f"<Job id={self.id} designation='{self.designation}' company_id={self.company_id}>"
