from datetime import UTC, datetime, time, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from study_tracker.application.exceptions import InvalidTimezoneError
from study_tracker.domain.enums.history_period import HistoryPeriod
from study_tracker.domain.enums.period import Period


class DateRangeService:

    def get_summary_range(
        self,
        timezone: str,
        period: Period,
    ) -> tuple[datetime | None, datetime | None]:

        user_timezone = self._get_timezone(timezone)

        if period == Period.ALL_TIME:
            return None, None

        now = datetime.now(user_timezone)

        if period == Period.TODAY:
            start_local, end_local = self._calendar_day_range(
                now,
                user_timezone,
            )

        elif period == Period.THIS_WEEK:
            start_local, end_local = self._calendar_week_range(
                now,
                user_timezone,
            )

        else:
            raise ValueError(f"Unsupported summary period: {period}")

        return self._to_utc_range(
            start_local,
            end_local,
        )

    def get_history_range(
        self,
        timezone: str,
        period: HistoryPeriod,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> tuple[datetime | None, datetime | None]:

        user_timezone = self._get_timezone(timezone)

        if period == HistoryPeriod.ALL_TIME:
            return None, None

        if period == HistoryPeriod.CUSTOM:
            return self._custom_range(
                start_date=start_date,
                end_date=end_date,
                user_timezone=user_timezone,
            )

        now = datetime.now(user_timezone)

        if period == HistoryPeriod.TODAY:
            start_local, end_local = self._calendar_day_range(
                now,
                user_timezone,
            )

        elif period == HistoryPeriod.THIS_WEEK:
            start_local, end_local = self._calendar_week_range(
                now,
                user_timezone,
            )

        elif period == HistoryPeriod.THIS_MONTH:
            start_local, end_local = self._calendar_month_range(
                now,
                user_timezone,
            )

        elif period == HistoryPeriod.LAST_7_DAYS:
            start_local = now - timedelta(days=7)
            end_local = now

        elif period == HistoryPeriod.LAST_30_DAYS:
            start_local = now - timedelta(days=30)
            end_local = now

        else:
            raise ValueError(f"Unsupported history period: {period}")

        return self._to_utc_range(
            start_local,
            end_local,
        )

    @staticmethod
    def _get_timezone(timezone: str) -> ZoneInfo:
        try:
            return ZoneInfo(timezone)
        except (ZoneInfoNotFoundError, ValueError):
            raise InvalidTimezoneError(timezone)

    @staticmethod
    def _calendar_day_range(
        now: datetime,
        user_timezone: ZoneInfo,
    ) -> tuple[datetime, datetime]:

        start_local = datetime.combine(
            now.date(),
            time.min,
            tzinfo=user_timezone,
        )

        end_local = start_local + timedelta(days=1)

        return start_local, end_local

    @staticmethod
    def _calendar_week_range(
        now: datetime,
        user_timezone: ZoneInfo,
    ) -> tuple[datetime, datetime]:

        start_local = datetime.combine(
            now.date() - timedelta(days=now.weekday()),
            time.min,
            tzinfo=user_timezone,
        )

        end_local = start_local + timedelta(days=7)

        return start_local, end_local

    @staticmethod
    def _calendar_month_range(
        now: datetime,
        user_timezone: ZoneInfo,
    ) -> tuple[datetime, datetime]:

        start_local = datetime(
            now.year,
            now.month,
            1,
            tzinfo=user_timezone,
        )

        if now.month == 12:
            end_local = datetime(
                now.year + 1,
                1,
                1,
                tzinfo=user_timezone,
            )
        else:
            end_local = datetime(
                now.year,
                now.month + 1,
                1,
                tzinfo=user_timezone,
            )

        return start_local, end_local

    @staticmethod
    def _custom_range(
        start_date: datetime | None,
        end_date: datetime | None,
        user_timezone: ZoneInfo,
    ) -> tuple[datetime, datetime]:

        if start_date is None or end_date is None:
            raise ValueError(
                "start_date and end_date are required " "for custom period"
            )

        if start_date.tzinfo is None:
            start_date = start_date.replace(tzinfo=user_timezone)

        if end_date.tzinfo is None:
            end_date = end_date.replace(tzinfo=user_timezone)

        end_date = end_date + timedelta(days=1)

        return DateRangeService._to_utc_range(
            start_date,
            end_date,
        )

    @staticmethod
    def _to_utc_range(
        start_local: datetime,
        end_local: datetime,
    ) -> tuple[datetime, datetime]:

        return (
            start_local.astimezone(UTC),
            end_local.astimezone(UTC),
        )
