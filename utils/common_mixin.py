from datetime import datetime

from sqlalchemy import Column, DateTime, Boolean, Integer


class CommonMixin:
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_deleted = Column(Boolean, default=False, nullable=False)


    # Created BY
    # created_by = Column(Integer, nullable=True)
    # Updated BY
    # updated_by = Column(Integer, nullable=True)