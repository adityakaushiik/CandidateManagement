from enum import Enum


class UserRoles(Enum):
    ADMIN = 1
    SUB_ADMIN = 2
    CANDIDATE = 3


class StatusInfo(Enum):
    ACTIVE = 1
    INACTIVE = 0
