from datetime import datetime

from sqlalchemy import func, select, text
from sqlalchemy.orm import Session
from study_tracker.domain.entities.study_session import StudySession
from study_tracker.domain.enums.group_by import GroupBy
from study_tracker.domain.enums.study_session_status import (
    StudySessionStatus,
)
from study_tracker.domain.repositories.analytics_repository import (
    AnalyticsRepository,
    GroupedSessionResult,
    RecentActivityResult,
)
from study_tracker.infrastructure.database.models.study_session import (
    StudySession as StudySessionModel,
)
from study_tracker.infrastructure.database.models.subject import (
    Subject as SubjectModel,
)


class SQLAlchemyAnalyticsRepository(AnalyticsRepository):

    def __init__(self, session: Session):
        self.session = session

    def get_total(
        self,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        subject_id: int | None = None,
    ) -> int:

        query = select(
            func.coalesce(
                func.sum(StudySessionModel.duration_seconds),
                0,
            )
        ).where(StudySessionModel.status == StudySessionStatus.FINISHED)

        if start_date is not None:
            query = query.where(StudySessionModel.started_at >= start_date)

        if end_date is not None:
            query = query.where(StudySessionModel.started_at < end_date)

        if subject_id is not None:
            query = query.where(StudySessionModel.subject_id == subject_id)

        total = self.session.scalar(query)

        return int(total or 0)

    def get_top_subjects(
        self,
        limit: int,
    ) -> list[tuple[str, int]]:

        total_duration = func.sum(StudySessionModel.duration_seconds)

        query = (
            select(
                SubjectModel.name,
                total_duration,
            )
            .join(
                StudySessionModel,
                StudySessionModel.subject_id == SubjectModel.id,
            )
            .where(StudySessionModel.status == StudySessionStatus.FINISHED)
            .group_by(
                SubjectModel.id,
                SubjectModel.name,
            )
            .order_by(
                total_duration.desc(),
                SubjectModel.id.desc(),
            )
            .limit(limit)
        )

        results = self.session.execute(query).all()

        return [(name, int(total_duration)) for name, total_duration in results]

    def get_recent_activity(
        self,
        limit: int,
    ) -> list[RecentActivityResult]:

        query = (
            select(
                StudySessionModel.id.label("session_id"),
                SubjectModel.id.label("subject_id"),
                SubjectModel.name.label("subject_name"),
                StudySessionModel.started_at.label("started_at"),
                StudySessionModel.duration_seconds.label("duration_seconds"),
            )
            .join(
                SubjectModel,
                StudySessionModel.subject_id == SubjectModel.id,
            )
            .where(StudySessionModel.status == StudySessionStatus.FINISHED)
            .order_by(
                StudySessionModel.started_at.desc(),
                StudySessionModel.id.desc(),
            )
            .limit(limit)
        )

        results = self.session.execute(query).all()

        return [
            RecentActivityResult(
                session_id=session_id,
                subject_id=subject_id,
                subject_name=subject_name,
                started_at=started_at,
                duration_seconds=int(duration_seconds),
            )
            for (
                session_id,
                subject_id,
                subject_name,
                started_at,
                duration_seconds,
            ) in results
        ]

    def get_sessions(
        self,
        subject_id: int | None = None,
        sub_subject_id: int | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> list[StudySession]:

        query = (
            select(StudySessionModel)
            .where(StudySessionModel.status == StudySessionStatus.FINISHED)
            .order_by(
                StudySessionModel.started_at.desc(),
                StudySessionModel.id.desc(),
            )
            .offset(offset)
            .limit(limit)
        )

        if subject_id is not None:
            query = query.where(StudySessionModel.subject_id == subject_id)

        if sub_subject_id is not None:
            query = query.where(StudySessionModel.sub_subject_id == sub_subject_id)

        if start_date is not None:
            query = query.where(StudySessionModel.started_at >= start_date)

        if end_date is not None:
            query = query.where(StudySessionModel.started_at < end_date)

        models = self.session.scalars(query).all()

        return [
            StudySession(
                id=model.id,
                subject_id=model.subject_id,
                sub_subject_id=model.sub_subject_id,
                started_at=model.started_at,
                ended_at=model.ended_at,
                duration_seconds=model.duration_seconds,
                created_at=model.created_at,
                status=model.status,
                paused_at=model.paused_at,
                paused_duration_seconds=model.paused_duration_seconds,
            )
            for model in models
        ]

    def get_grouped_sessions(
        self,
        timezone: str,
        subject_id: int | None = None,
        sub_subject_id: int | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        group_by: GroupBy = GroupBy.DAY,
    ) -> list[GroupedSessionResult]:

        local_started_at = StudySessionModel.started_at.op("AT TIME ZONE")(timezone)

        if group_by == GroupBy.DAY:
            period_start = func.date_trunc(
                "day",
                local_started_at,
            )

            period_end = period_start + text("interval '1 day'")

        elif group_by == GroupBy.WEEK:
            period_start = func.date_trunc(
                "week",
                local_started_at,
            )

            period_end = period_start + text("interval '7 days'")

        elif group_by == GroupBy.MONTH:
            period_start = func.date_trunc(
                "month",
                local_started_at,
            )

            period_end = period_start + text("interval '1 month'")

        else:
            raise ValueError(f"Unsupported group_by: {group_by}")

        total_duration = func.sum(StudySessionModel.duration_seconds)

        session_count = func.count(StudySessionModel.id)

        query = (
            select(
                period_start.label("period_start"),
                period_end.label("period_end"),
                SubjectModel.id.label("subject_id"),
                SubjectModel.name.label("subject_name"),
                total_duration.label("duration_seconds"),
                session_count.label("session_count"),
            )
            .join(
                SubjectModel,
                StudySessionModel.subject_id == SubjectModel.id,
            )
            .where(StudySessionModel.status == StudySessionStatus.FINISHED)
        )

        if subject_id is not None:
            query = query.where(StudySessionModel.subject_id == subject_id)

        if sub_subject_id is not None:
            query = query.where(StudySessionModel.sub_subject_id == sub_subject_id)

        if start_date is not None:
            query = query.where(StudySessionModel.started_at >= start_date)

        if end_date is not None:
            query = query.where(StudySessionModel.started_at < end_date)

        query = query.group_by(
            period_start,
            period_end,
            SubjectModel.id,
            SubjectModel.name,
        ).order_by(
            period_start.desc(),
            SubjectModel.id.asc(),
        )

        results = self.session.execute(query).all()

        return [
            GroupedSessionResult(
                period_start=period_start_value,
                period_end=period_end_value,
                subject_id=subject_id,
                subject_name=subject_name,
                duration_seconds=int(duration_seconds),
                session_count=int(session_count),
            )
            for (
                period_start_value,
                period_end_value,
                subject_id,
                subject_name,
                duration_seconds,
                session_count,
            ) in results
        ]

    def count_sessions(
        self,
        subject_id: int | None = None,
        sub_subject_id: int | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> int:

        query = select(func.count(StudySessionModel.id)).where(
            StudySessionModel.status == StudySessionStatus.FINISHED
        )

        if subject_id is not None:
            query = query.where(StudySessionModel.subject_id == subject_id)

        if sub_subject_id is not None:
            query = query.where(StudySessionModel.sub_subject_id == sub_subject_id)

        if start_date is not None:
            query = query.where(StudySessionModel.started_at >= start_date)

        if end_date is not None:
            query = query.where(StudySessionModel.started_at < end_date)

        return int(self.session.scalar(query) or 0)
