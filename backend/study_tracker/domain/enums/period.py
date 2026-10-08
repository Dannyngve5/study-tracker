from enum import Enum


class Period(str, Enum):
    TODAY = "today"
    THIS_WEEK = "this_week"
    ALL_TIME = "all_time"
