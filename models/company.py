from sqlalchemy import Column, String, Text, Date
from sqlalchemy.orm import relationship

from config.database import Base
from utils.common_mixin import CommonMixin


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
    jobs = relationship(
        "JobModel",  # The related model class name
        back_populates="company",  # Name of the reverse relationship attribute in JobModel that references this CompanyModel
        cascade="all, delete-orphan"  # Automatically delete all related jobs when company is deleted, and delete orphaned jobs
    )
    experiences = relationship(
        "Experience",  # The related model class name to establish relationship with Experience model
        # No back_populates since Experience doesn't have a reverse relationship defined
    )
