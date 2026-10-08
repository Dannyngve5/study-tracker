from study_tracker.application.dto.analytics import (
    AnalyticsSummaryDTO,
    GroupedSessionDTO,
    PaginatedSessionsDTO,
    RecentActivityDTO,
    TopSubjectDTO,
)
from study_tracker.application.dto.history import HistoryFiltersDTO
from study_tracker.application.services.date_range_service import (
    DateRangeService,
)
from study_tracker.domain.enums.group_by import GroupBy
from study_tracker.domain.enums.period import Period
from study_tracker.domain.repositories.unit_of_work import UnitOfWork


class AnalyticsService:

    def __init__(
        self,
        unit_of_work: UnitOfWork,
        date_range_service: DateRangeService | None = None,
    ):
        self.unit_of_work = unit_of_work
        self.date_range_service = date_range_service or DateRangeService()

    def get_summary(
        self,
        timezone: str,
        subject_id: int | None = None,
    ) -> AnalyticsSummaryDTO:

        today_start, today_end = self.date_range_service.get_summary_range(
            timezone=timezone,
            period=Period.TODAY,
        )

        this_week_start, this_week_end = self.date_range_service.get_summary_range(
            timezone=timezone,
            period=Period.THIS_WEEK,
        )

        with self.unit_of_work as uow:
            today_seconds = uow.analytics.get_total(
                start_date=today_start,
                end_date=today_end,
                subject_id=subject_id,
            )

            this_week_seconds = uow.analytics.get_total(
                start_date=this_week_start,
                end_date=this_week_end,
                subject_id=subject_id,
            )

            all_time_seconds = uow.analytics.get_total(
                subject_id=subject_id,
            )

            top_subjects = [
                TopSubjectDTO(
                    subject_name=subject_name,
                    duration_seconds=duration_seconds,
                )
                for subject_name, duration_seconds in uow.analytics.get_top_subjects(
                    limit=5
                )
            ]

            recent_activity = [
                RecentActivityDTO(
                    session_id=result.session_id,
                    subject_id=result.subject_id,
                    subject_name=result.subject_name,
                    started_at=result.started_at,
                    duration_seconds=result.duration_seconds,
                )
                for result in uow.analytics.get_recent_activity(limit=5)
            ]

            return AnalyticsSummaryDTO(
                today_seconds=today_seconds,
                this_week_seconds=this_week_seconds,
                all_time_seconds=all_time_seconds,
                top_subjects=top_subjects,
                recent_activity=recent_activity,
            )

    def get_sessions(
        self,
        filters: HistoryFiltersDTO,
        timezone: str,
        offset: int = 0,
        limit: int = 50,
    ) -> PaginatedSessionsDTO:

        start_date, end_date = self.date_range_service.get_history_range(
            timezone=timezone,
            period=filters.period,
            start_date=filters.start_date,
            end_date=filters.end_date,
        )

        with self.unit_of_work as uow:
            total = uow.analytics.count_sessions(
                subject_id=filters.subject_id,
                sub_subject_id=filters.sub_subject_id,
                start_date=start_date,
                end_date=end_date,
            )

            items = uow.analytics.get_sessions(
                subject_id=filters.subject_id,
                sub_subject_id=filters.sub_subject_id,
                start_date=start_date,
                end_date=end_date,
                offset=offset,
                limit=limit,
            )

            return PaginatedSessionsDTO(
                items=items,
                total=total,
                offset=offset,
                limit=limit,
                has_more=offset + len(items) < total,
            )

    def get_grouped_sessions(
        self,
        filters: HistoryFiltersDTO,
        timezone: str,
        group_by: GroupBy,
    ) -> list[GroupedSessionDTO]:

        start_date, end_date = self.date_range_service.get_history_range(
            timezone=timezone,
            period=filters.period,
            start_date=filters.start_date,
            end_date=filters.end_date,
        )

        with self.unit_of_work as uow:
            results = uow.analytics.get_grouped_sessions(
                timezone=timezone,
                subject_id=filters.subject_id,
                sub_subject_id=filters.sub_subject_id,
                start_date=start_date,
                end_date=end_date,
                group_by=group_by,
            )

            return [
                GroupedSessionDTO(
                    period_start=result.period_start,
                    period_end=result.period_end,
                    subject_id=result.subject_id,
                    subject_name=result.subject_name,
                    duration_seconds=result.duration_seconds,
                    session_count=result.session_count,
                )
                for result in results
            ]
