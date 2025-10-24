from sqlalchemy import Column, String, Text, Date
from sqlalchemy.orm import relationship

from config.database import Base
from models.common_mixin import CommonMixin


class CompanyModel(Base, CommonMixin):
    """Postgres-backed Company DB model."""
    __tablename__ = "companies"

    name = Column(String(200), nullable=False)
    website_url = Column(String(300))
    logo_url = Column(String(300))
    description = Column(Text)
    headquarters = Column(String(200))
    member_since = Column(Date)

    # Relationship to jobs (one company -> many jobs)
    jobs = relationship("JobModel", back_populates="company", cascade="all, delete-orphan")
