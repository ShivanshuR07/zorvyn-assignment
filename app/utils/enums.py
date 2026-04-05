from enum import Enum


class RoleEnum(str, Enum):
    viewer = "viewer"
    analyst = "analyst"
    admin = "admin"


class UserStateEnum(str, Enum):
    active = "active"
    inactive = "inactive"
    suspended = "suspended"


class RecordTypeEnum(str, Enum):
    income = "income"
    expense = "expense"


class TrendPeriodEnum(str, Enum):
    weekly = "weekly"
    monthly = "monthly"


class TrendTypeFilterEnum(str, Enum):
    all = "all"
    income = "income"
    expense = "expense"
