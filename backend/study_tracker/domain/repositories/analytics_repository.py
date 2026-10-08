from abc import ABC, abstractmethod
from datetime import datetime
from typing import NamedTuple

from study_tracker.domain.entities.study_session import StudySession
from study_tracker.domain.enums.group_by import GroupBy


class RecentActivityResult(NamedTuple):
    session_id: int
    subject_id: int
    subject_name: str
    started_at: datetime
    duration_seconds: int


class GroupedSessionResult(NamedTuple):
    period_start: datetime
    period_end: datetime
    subject_id: int
    subject_name: str
    duration_seconds: int
    session_count: int


class AnalyticsRepository(ABC):

    @abstractmethod
    def get_total(
        self,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        subject_id: int | None = None,
    ) -> int:
        pass

    @abstractmethod
    def get_top_subjects(
        self,
        limit: int,
    ) -> list[tuple[str, int]]:
        pass

    @abstractmethod
    def get_recent_activity(
        self,
        limit: int,
    ) -> list[RecentActivityResult]:
        pass

    @abstractmethod
    def get_sessions(
        self,
        subject_id: int | None = None,
        sub_subject_id: int | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> list[StudySession]:
        pass

    @abstractmethod
    def get_grouped_sessions(
        self,
        timezone: str,
        subject_id: int | None = None,
        sub_subject_id: int | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        group_by: GroupBy = GroupBy.DAY,
    ) -> list[GroupedSessionResult]:
        pass

    @abstractmethod
    def count_sessions(
        self,
        subject_id: int | None = None,
        sub_subject_id: int | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> int:
        pass
