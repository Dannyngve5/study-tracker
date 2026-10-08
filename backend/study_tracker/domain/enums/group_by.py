from enum import Enum


class GroupBy(str, Enum):
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
