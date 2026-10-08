from enum import Enum


class HistoryPeriod(str, Enum):
    TODAY = "today"
    THIS_WEEK = "this_week"
    THIS_MONTH = "this_month"
    LAST_7_DAYS = "last_7_days"
    LAST_30_DAYS = "last_30_days"
    ALL_TIME = "all_time"
    CUSTOM = "custom"
