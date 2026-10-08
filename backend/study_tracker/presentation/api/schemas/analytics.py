from datetime import datetime

from pydantic import BaseModel, ConfigDict
from study_tracker.presentation.api.schemas.study_session import (
    StudySessionResponse,
)


class TopSubjectResponse(BaseModel):
    subject_name: str
    duration_seconds: int


class RecentActivityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    session_id: int
    subject_id: int
    subject_name: str
    started_at: datetime
    duration_seconds: int


class GroupedSessionResponse(BaseModel):
    period_start: datetime
    period_end: datetime
    subject_id: int
    subject_name: str
    duration_seconds: int
    session_count: int


class AnalyticsSummaryResponse(BaseModel):
    today_seconds: int
    this_week_seconds: int
    all_time_seconds: int
    top_subjects: list[TopSubjectResponse]
    recent_activity: list[RecentActivityResponse]


class PaginatedSessionsResponse(BaseModel):
    items: list[StudySessionResponse]
    total: int
    offset: int
    limit: int
    has_more: bool
