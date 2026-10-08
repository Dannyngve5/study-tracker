from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import MagicMock

from study_tracker.application.dto.history import HistoryFiltersDTO
from study_tracker.application.services.analytics_service import AnalyticsService
from study_tracker.domain.enums.group_by import GroupBy
from study_tracker.domain.enums.history_period import HistoryPeriod
from study_tracker.domain.repositories.analytics_repository import (
    GroupedSessionResult,
    RecentActivityResult,
)


def make_service():
    analytics_repository = MagicMock()
    unit_of_work = MagicMock()
    unit_of_work.__enter__.return_value = unit_of_work
    unit_of_work.analytics = analytics_repository

    date_range_service = MagicMock()
    date_range_service.get_summary_range.side_effect = [
        (
            datetime(2026, 10, 8, 4, 0, tzinfo=UTC),
            datetime(2026, 10, 9, 4, 0, tzinfo=UTC),
        ),
        (
            datetime(2026, 10, 5, 4, 0, tzinfo=UTC),
            datetime(2026, 10, 12, 4, 0, tzinfo=UTC),
        ),
    ]
    date_range_service.get_history_range.return_value = (
        datetime(2026, 10, 1, tzinfo=UTC),
        datetime(2026, 11, 1, tzinfo=UTC),
    )

    return (
        AnalyticsService(unit_of_work, date_range_service),
        unit_of_work,
        analytics_repository,
        date_range_service,
    )


def test_get_summary_returns_totals_top_subjects_and_recent_activity():
    service, unit_of_work, repository, date_range_service = make_service()
    repository.get_total.side_effect = [3600, 7200, 18000]
    repository.get_top_subjects.return_value = [
        ("Python", 9000),
        ("Math", 7000),
    ]
    repository.get_recent_activity.return_value = [
        RecentActivityResult(
            session_id=8,
            subject_id=3,
            subject_name="Python",
            started_at=datetime(2026, 10, 8, 10, 0, tzinfo=UTC),
            duration_seconds=1800,
        )
    ]

    result = service.get_summary(timezone="America/New_York", subject_id=3)

    assert result.today_seconds == 3600
    assert result.this_week_seconds == 7200
    assert result.all_time_seconds == 18000
    assert [item.subject_name for item in result.top_subjects] == ["Python", "Math"]
    assert result.recent_activity[0].session_id == 8
    assert result.recent_activity[0].subject_name == "Python"
    assert repository.get_total.call_count == 3
    assert repository.get_total.call_args_list[0].kwargs == {
        "start_date": datetime(2026, 10, 8, 4, 0, tzinfo=UTC),
        "end_date": datetime(2026, 10, 9, 4, 0, tzinfo=UTC),
        "subject_id": 3,
    }
    assert repository.get_total.call_args_list[1].kwargs["subject_id"] == 3
    assert repository.get_total.call_args_list[2].kwargs == {"subject_id": 3}
    repository.get_top_subjects.assert_called_once_with(limit=5)
    repository.get_recent_activity.assert_called_once_with(limit=5)
    assert date_range_service.get_summary_range.call_count == 2
    unit_of_work.__enter__.assert_called_once()


def test_get_sessions_applies_filters_and_returns_pagination_metadata():
    service, _, repository, date_range_service = make_service()
    repository.count_sessions.return_value = 3
    repository.get_sessions.return_value = [SimpleNamespace(id=11), SimpleNamespace(id=10)]
    filters = HistoryFiltersDTO(
        subject_id=4,
        period=HistoryPeriod.THIS_MONTH,
    )

    result = service.get_sessions(
        filters=filters,
        timezone="UTC",
        offset=1,
        limit=2,
    )

    assert [item.id for item in result.items] == [11, 10]
    assert result.total == 3
    assert result.offset == 1
    assert result.limit == 2
    assert result.has_more is False
    assert repository.count_sessions.call_args.kwargs == {
        "subject_id": 4,
        "sub_subject_id": None,
        "start_date": datetime(2026, 10, 1, tzinfo=UTC),
        "end_date": datetime(2026, 11, 1, tzinfo=UTC),
    }
    assert repository.get_sessions.call_args.kwargs == {
        "subject_id": 4,
        "sub_subject_id": None,
        "start_date": datetime(2026, 10, 1, tzinfo=UTC),
        "end_date": datetime(2026, 11, 1, tzinfo=UTC),
        "offset": 1,
        "limit": 2,
    }
    date_range_service.get_history_range.assert_called_once_with(
        timezone="UTC",
        period=HistoryPeriod.THIS_MONTH,
        start_date=None,
        end_date=None,
    )


def test_get_sessions_sets_has_more_when_another_page_exists():
    service, _, repository, _ = make_service()
    repository.count_sessions.return_value = 5
    repository.get_sessions.return_value = [SimpleNamespace(id=1), SimpleNamespace(id=2)]

    result = service.get_sessions(
        filters=HistoryFiltersDTO(),
        timezone="UTC",
        offset=0,
        limit=2,
    )

    assert result.has_more is True


def test_get_grouped_sessions_maps_repository_results_to_dtos():
    service, _, repository, _ = make_service()
    repository.get_grouped_sessions.return_value = [
        GroupedSessionResult(
            period_start=datetime.fromisoformat("2026-10-08"),
            period_end=datetime.fromisoformat("2026-10-09"),
            subject_id=4,
            subject_name="Python",
            duration_seconds=5400,
            session_count=3,
        )
    ]

    result = service.get_grouped_sessions(
        filters=HistoryFiltersDTO(
            subject_id=4,
            period=HistoryPeriod.CUSTOM,
            start_date=datetime.fromisoformat("2026-10-08"),
            end_date=datetime.fromisoformat("2026-10-08"),
        ),
        timezone="America/New_York",
        group_by=GroupBy.DAY,
    )

    assert len(result) == 1
    assert result[0].subject_name == "Python"
    assert result[0].duration_seconds == 5400
    assert result[0].session_count == 3
    repository.get_grouped_sessions.assert_called_once_with(
        timezone="America/New_York",
        subject_id=4,
        sub_subject_id=None,
        start_date=datetime(2026, 10, 1, tzinfo=UTC),
        end_date=datetime(2026, 11, 1, tzinfo=UTC),
        group_by=GroupBy.DAY,
    )
