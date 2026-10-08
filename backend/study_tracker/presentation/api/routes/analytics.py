from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from study_tracker.application.dto.history import HistoryFiltersDTO
from study_tracker.application.services.analytics_service import (
    AnalyticsService,
)
from study_tracker.domain.enums.group_by import GroupBy
from study_tracker.domain.enums.history_mode import HistoryMode
from study_tracker.domain.enums.history_period import HistoryPeriod
from study_tracker.presentation.api.dependencies import (
    get_analytics_service,
)
from study_tracker.presentation.api.schemas.analytics import (
    AnalyticsSummaryResponse,
    GroupedSessionResponse,
    PaginatedSessionsResponse,
)

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
)


def get_history_filters(
    subject_id: Annotated[int | None, Query(gt=0)] = None,
    sub_subject_id: Annotated[int | None, Query(gt=0)] = None,
    period: Annotated[
        HistoryPeriod,
        Query(),
    ] = HistoryPeriod.ALL_TIME,
    mode: Annotated[
        HistoryMode,
        Query(),
    ] = HistoryMode.INDIVIDUAL,
    start_date: Annotated[datetime | None, Query()] = None,
    end_date: Annotated[datetime | None, Query()] = None,
) -> HistoryFiltersDTO:
    try:
        return HistoryFiltersDTO(
            subject_id=subject_id,
            sub_subject_id=sub_subject_id,
            period=period,
            mode=mode,
            start_date=start_date,
            end_date=end_date,
        )
    except ValidationError as exc:
        raise RequestValidationError(exc.errors()) from exc


@router.get(
    "/summary",
    response_model=AnalyticsSummaryResponse,
)
def get_analytics_summary(
    service: Annotated[
        AnalyticsService,
        Depends(get_analytics_service),
    ],
    timezone: Annotated[str, Query()],
    subject_id: Annotated[int | None, Query(gt=0)] = None,
) -> AnalyticsSummaryResponse:
    return service.get_summary(
        timezone=timezone,
        subject_id=subject_id,
    )


@router.get(
    "/sessions",
    response_model=(PaginatedSessionsResponse | list[GroupedSessionResponse]),
)
def get_analytics_sessions(
    service: Annotated[
        AnalyticsService,
        Depends(get_analytics_service),
    ],
    filters: Annotated[
        HistoryFiltersDTO,
        Depends(get_history_filters),
    ],
    timezone: Annotated[str, Query()],
    group_by: Annotated[
        GroupBy,
        Query(),
    ] = GroupBy.DAY,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
):
    if filters.mode == HistoryMode.INDIVIDUAL:
        result = service.get_sessions(
            filters=filters,
            timezone=timezone,
            offset=offset,
            limit=limit,
        )

        return PaginatedSessionsResponse(
            items=result.items,
            total=result.total,
            offset=result.offset,
            limit=result.limit,
            has_more=result.has_more,
        )

    return [
        GroupedSessionResponse(
            period_start=result.period_start,
            period_end=result.period_end,
            subject_id=result.subject_id,
            subject_name=result.subject_name,
            duration_seconds=result.duration_seconds,
            session_count=result.session_count,
        )
        for result in service.get_grouped_sessions(
            filters=filters,
            timezone=timezone,
            group_by=group_by,
        )
    ]
