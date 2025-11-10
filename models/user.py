from sqlalchemy import Column, String, Boolean, Integer
from sqlalchemy.orm import relationship

from config.database import Base
from utils.common_mixin import CommonMixin


class UserModel(Base, CommonMixin):
    """Postgres-backed User DB model."""

    __tablename__ = "users"

    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=True)

    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, unique=True, index=True, nullable=False)

    hashed_password = Column(String, nullable=False)
    profile_picture_url = Column(String, nullable=True)

    role_id = Column(Integer, nullable=False)

    blacklisted = Column(Boolean, nullable=True, default=False)

    # Relationships
    candidate = relationship(
        "CandidateModel",  # The related model class name to establish relationship with CandidateModel
        back_populates="user",  # Name of the reverse relationship attribute in CandidateModel that references this UserModel
        uselist=False,  # One-to-one relationship - a user has only one candidate profile
    )
    user_schedules = relationship(
        "UserScheduleModel",  # The related model class name to establish relationship with UserScheduleModel
        back_populates="user",  # Name of the reverse relationship attribute in UserScheduleModel that references this UserModel
    )
