from sqlalchemy import Column, String, Text
from sqlalchemy.orm import relationship

from config.database import Base
from utils.common_mixin import CommonMixin


class ScheduleProcessModel(Base, CommonMixin):
    """Defines a scheduled process or step used in `UserSchedule`."""

    __tablename__ = "schedule_processes"

    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)

    # Relationship back to user schedules
    user_schedules = relationship(
        "UserScheduleModel",  # The related model class name to establish relationship with UserScheduleModel
        back_populates="schedule_process",  # Name of the reverse relationship attribute in UserScheduleModel that references this ScheduleProcessModel
        cascade="all, delete-orphan",  # Automatically delete all related user schedules when schedule process is deleted, and delete orphaned schedules
    )

    def __repr__(self) -> str:  # pragma: no cover - trivial
        return f"<ScheduleProcess id={self.id} title='{self.title}'>"
