from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship

from config.database import Base
from models.common_mixin import CommonMixin


class Experience(Base, CommonMixin):
    __tablename__ = "experiences"

    # replace PyObjectId with a SQL FK to companies (adjust table/name as needed)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    role = Column(String(200), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)
    description = Column(Text, nullable=True)

    company = relationship("Company", lazy="joined")
