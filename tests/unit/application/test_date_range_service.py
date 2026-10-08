from datetime import UTC, datetime

import pytest
from study_tracker.application.dto.history import HistoryFiltersDTO
from study_tracker.application.exceptions import InvalidTimezoneError
from study_tracker.application.services.date_range_service import DateRangeService
from study_tracker.domain.enums.history_period import HistoryPeriod
from study_tracker.domain.enums.period import Period


class FixedDateTime(datetime):
    current = datetime(2026, 10, 8, 15, 30, tzinfo=UTC)

    @classmethod
    def now(cls, tz=None):
        if tz is None:
            return cls.current.replace(tzinfo=None)

        return cls.current.astimezone(tz)


def test_get_summary_range_returns_calendar_day_in_user_timezone(monkeypatch):
    monkeypatch.setattr(
        "study_tracker.application.services.date_range_service.datetime",
        FixedDateTime,
    )

    start_date, end_date = DateRangeService().get_summary_range(
        timezone="America/New_York",
        period=Period.TODAY,
    )

    assert start_date == datetime(2026, 10, 8, 4, 0, tzinfo=UTC)
    assert end_date == datetime(2026, 10, 9, 4, 0, tzinfo=UTC)


def test_get_summary_range_uses_monday_as_start_of_week(monkeypatch):
    monkeypatch.setattr(
        "study_tracker.application.services.date_range_service.datetime",
        FixedDateTime,
    )

    start_date, end_date = DateRangeService().get_summary_range(
        timezone="America/New_York",
        period=Period.THIS_WEEK,
    )

    assert start_date == datetime(2026, 10, 5, 4, 0, tzinfo=UTC)
    assert end_date == datetime(2026, 10, 12, 4, 0, tzinfo=UTC)


def test_get_summary_range_returns_no_bounds_for_all_time():
    assert DateRangeService().get_summary_range(
        timezone="UTC",
        period=Period.ALL_TIME,
    ) == (None, None)


def test_get_history_range_includes_both_custom_calendar_dates_across_dst():
    start_date, end_date = DateRangeService().get_history_range(
        timezone="America/New_York",
        period=HistoryPeriod.CUSTOM,
        start_date=datetime.fromisoformat("2026-03-07"),
        end_date=datetime.fromisoformat("2026-03-08"),
    )

    assert start_date == datetime(2026, 3, 7, 5, 0, tzinfo=UTC)
    assert end_date == datetime(2026, 3, 9, 4, 0, tzinfo=UTC)


def test_get_history_range_returns_no_bounds_for_all_time():
    assert DateRangeService().get_history_range(
        timezone="UTC",
        period=HistoryPeriod.ALL_TIME,
    ) == (None, None)


@pytest.mark.parametrize("timezone", ["Not/A_Timezone", "\x00"])
def test_get_history_range_rejects_invalid_timezone(timezone):
    with pytest.raises(InvalidTimezoneError):
        DateRangeService().get_history_range(
            timezone=timezone,
            period=HistoryPeriod.TODAY,
        )


def test_history_filters_require_dates_for_custom_period():
    with pytest.raises(ValueError, match="start_date and end_date are required"):
        HistoryFiltersDTO(period=HistoryPeriod.CUSTOM)


def test_history_filters_reject_end_date_before_start_date():
    with pytest.raises(ValueError, match="end_date cannot be earlier"):
        HistoryFiltersDTO(
            period=HistoryPeriod.CUSTOM,
            start_date=datetime.fromisoformat("2026-10-09"),
            end_date=datetime.fromisoformat("2026-10-08"),
        )
