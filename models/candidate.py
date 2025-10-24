from sqlalchemy import Column, String, DateTime, Float, Text
from sqlalchemy.dialects.postgresql import JSONB

from config.database import Base
from models.common_mixin import CommonMixin


class CandidateBase(Base, CommonMixin):
    __tablename__ = "candidates"

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
