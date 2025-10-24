from sqlalchemy import Column, String, Boolean

from config.database import Base
from models.common_mixin import CommonMixin


class UserModel(Base, CommonMixin):
    """Postgres-backed User DB model."""
    __tablename__ = "users"

    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=True)

    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, unique=True, index=True, nullable=False)

    hashed_password = Column(String, nullable=False)
    profile_picture_url = Column(String, nullable=True)

    blacklisted = Column(Boolean, nullable=True, default=False)
