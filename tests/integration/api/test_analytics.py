from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient
from study_tracker.application.dto.analytics import (
    AnalyticsSummaryDTO,
    GroupedSessionDTO,
    PaginatedSessionsDTO,
    RecentActivityDTO,
    TopSubjectDTO,
)
from study_tracker.application.services.analytics_service import AnalyticsService
from study_tracker.main import app
from study_tracker.presentation.api.dependencies import get_analytics_service


class FakeAnalyticsService:
    def __init__(self):
        self.summary_args = None
        self.sessions_args = None
        self.grouped_args = None

    def get_summary(self, timezone: str, subject_id: int | None = None):
        self.summary_args = {"timezone": timezone, "subject_id": subject_id}
        return AnalyticsSummaryDTO(
            today_seconds=3600,
            this_week_seconds=7200,
            all_time_seconds=18000,
            top_subjects=[
                TopSubjectDTO(subject_name="Python", duration_seconds=9000)
            ],
            recent_activity=[
                RecentActivityDTO(
                    session_id=7,
                    subject_id=2,
                    subject_name="Python",
                    started_at=datetime(2026, 10, 8, 10, 0, tzinfo=UTC),
                    duration_seconds=1800,
                )
            ],
        )

    def get_sessions(
        self,
        filters,
        timezone: str,
        offset: int = 0,
        limit: int = 50,
    ):
        self.sessions_args = {
            "filters": filters,
            "timezone": timezone,
            "offset": offset,
            "limit": limit,
        }
        return PaginatedSessionsDTO(
            items=[],
            total=0,
            offset=offset,
            limit=limit,
            has_more=False,
        )

    def get_grouped_sessions(self, filters, timezone: str, group_by):
        self.grouped_args = {
            "filters": filters,
            "timezone": timezone,
            "group_by": group_by,
        }
        return [
            GroupedSessionDTO(
                period_start=datetime.fromisoformat("2026-10-08"),
                period_end=datetime.fromisoformat("2026-10-09"),
                subject_id=2,
                subject_name="Python",
                duration_seconds=5400,
                session_count=3,
            )
        ]


@pytest.fixture
def api_client():
    service = FakeAnalyticsService()
    app.dependency_overrides[get_analytics_service] = lambda: service

    with TestClient(app, raise_server_exceptions=False) as client:
        yield client, service

    app.dependency_overrides.pop(get_analytics_service, None)


def test_summary_endpoint_returns_panels_and_forwards_subject_filter(api_client):
    client, service = api_client

    response = client.get(
        "/analytics/summary",
        params={"timezone": "America/New_York", "subject_id": 2},
    )

    assert response.status_code == 200
    assert response.json()["today_seconds"] == 3600
    assert response.json()["top_subjects"] == [
        {"subject_name": "Python", "duration_seconds": 9000}
    ]
    assert response.json()["recent_activity"][0]["session_id"] == 7
    assert service.summary_args == {
        "timezone": "America/New_York",
        "subject_id": 2,
    }


def test_individual_history_endpoint_returns_paginated_response(api_client):
    client, service = api_client

    response = client.get(
        "/analytics/sessions",
        params={
            "timezone": "UTC",
            "subject_id": 2,
            "period": "last_7_days",
            "mode": "individual",
            "offset": 10,
            "limit": 20,
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "items": [],
        "total": 0,
        "offset": 10,
        "limit": 20,
        "has_more": False,
    }
    assert service.sessions_args["filters"].subject_id == 2
    assert service.sessions_args["filters"].period.value == "last_7_days"
    assert service.sessions_args["filters"].mode.value == "individual"
    assert service.sessions_args["offset"] == 10
    assert service.sessions_args["limit"] == 20


def test_grouped_history_endpoint_returns_group_results(api_client):
    client, service = api_client

    response = client.get(
        "/analytics/sessions",
        params={
            "timezone": "UTC",
            "mode": "grouped",
            "group_by": "day",
        },
    )

    assert response.status_code == 200
    assert response.json() == [
        {
            "period_start": "2026-10-08T00:00:00",
            "period_end": "2026-10-09T00:00:00",
            "subject_id": 2,
            "subject_name": "Python",
            "duration_seconds": 5400,
            "session_count": 3,
        }
    ]
    assert service.grouped_args["group_by"].value == "day"
    assert service.sessions_args is None


def test_analytics_endpoints_return_400_for_invalid_timezone():
    app.dependency_overrides[get_analytics_service] = lambda: AnalyticsService(
        unit_of_work=None
    )

    try:
        with TestClient(app) as client:
            response = client.get(
                "/analytics/summary",
                params={"timezone": "Not/A_Timezone"},
            )
    finally:
        app.dependency_overrides.pop(get_analytics_service, None)

    assert response.status_code == 400
    assert response.json()["code"] == "INVALID_TIMEZONE"


@pytest.mark.parametrize(
    ("start_date", "end_date"),
    [
        ("2026-10-09", "2026-10-08"),
        ("2026-10-08", None),
    ],
)
def test_history_endpoint_returns_422_for_invalid_custom_range(
    api_client,
    start_date,
    end_date,
):
    client, _ = api_client
    params = {
        "timezone": "UTC",
        "period": "custom",
        "start_date": start_date,
    }
    if end_date is not None:
        params["end_date"] = end_date

    response = client.get("/analytics/sessions", params=params)

    assert response.status_code == 422
