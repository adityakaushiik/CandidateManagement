"""
Models package for Candidate Management System.

This module exports all SQLAlchemy ORM models used in the application.
"""

from models.candidate import CandidateModel
from models.candidate_skill import CandidateSkillModel
from models.company import CompanyModel
from models.job import JobModel, JoiningTime
from models.schedule_process import ScheduleProcessModel
from models.skill import SkillModel
from models.user import UserModel
from models.user_schedule import UserScheduleModel
from models.experience import ExperienceModel

__all__ = [
    # User and Authentication
    "UserModel",
    # Candidate related
    "CandidateModel",
    "CandidateSkillModel",
    # Company and Jobs
    "CompanyModel",
    "JobModel",
    "JoiningTime",
    # Skills
    "SkillModel",
    "ExperienceModel",
    # Scheduling
    "ScheduleProcessModel",
    "UserScheduleModel",
]
