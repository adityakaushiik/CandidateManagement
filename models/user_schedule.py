from sqlalchemy import Column, Integer, ForeignKey, Text
from sqlalchemy.orm import relationship

from config.database import Base
from utils.common_mixin import CommonMixin


class UserScheduleModel(Base, CommonMixin):
    """Associates a user with a job and an optional schedule process step."""
    __tablename__ = "user_schedules"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    schedule_process_id = Column(Integer, ForeignKey("schedule_processes.id", ondelete="SET NULL"), nullable=True, index=True)
    notes = Column(Text, nullable=True)

    # Relationships
    user = relationship(
        "UserModel"  # The related model class name to establish relationship with UserModel (one-sided, no back_populates to avoid modifying existing user model)
    )
    job = relationship(
        "JobModel",  # The related model class name to establish relationship with JobModel
        back_populates="user_schedules"  # Name of the reverse relationship attribute in JobModel that references this UserScheduleModel
    )
    schedule_process = relationship(
        "ScheduleProcessModel",  # The related model class name to establish relationship with ScheduleProcessModel
        back_populates="user_schedules"  # Name of the reverse relationship attribute in ScheduleProcessModel that references this UserScheduleModel
    )

    def __repr__(self) -> str:  # pragma: no cover - trivial
        return f"<UserSchedule id={self.id} user_id={self.user_id} job_id={self.job_id} schedule_process_id={self.schedule_process_id}>"
