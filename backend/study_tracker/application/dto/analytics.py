from datetime import datetime

from pydantic import BaseModel


class TopSubjectDTO(BaseModel):
    subject_name: str
    duration_seconds: int


class RecentActivityDTO(BaseModel):
    session_id: int
    subject_id: int
    subject_name: str
    started_at: datetime
    duration_seconds: int


class GroupedSessionDTO(BaseModel):
    period_start: datetime
    period_end: datetime
    subject_id: int
    subject_name: str
    duration_seconds: int
    session_count: int


class AnalyticsSummaryDTO(BaseModel):
    today_seconds: int
    this_week_seconds: int
    all_time_seconds: int
    top_subjects: list[TopSubjectDTO]
    recent_activity: list[RecentActivityDTO]


class PaginatedSessionsDTO(BaseModel):
    items: list
    total: int
    offset: int
    limit: int
    has_more: bool
