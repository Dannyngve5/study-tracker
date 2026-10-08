from datetime import datetime

from pydantic import BaseModel, Field, model_validator
from study_tracker.domain.enums.history_mode import HistoryMode
from study_tracker.domain.enums.history_period import HistoryPeriod


class HistoryFiltersDTO(BaseModel):
    subject_id: int | None = Field(default=None, gt=0)
    sub_subject_id: int | None = Field(default=None, gt=0)

    period: HistoryPeriod = HistoryPeriod.ALL_TIME
    mode: HistoryMode = HistoryMode.INDIVIDUAL

    start_date: datetime | None = None
    end_date: datetime | None = None

    @model_validator(mode="after")
    def validate_custom_range(self) -> "HistoryFiltersDTO":
        if self.period != HistoryPeriod.CUSTOM:
            return self

        if self.start_date is None or self.end_date is None:
            raise ValueError("start_date and end_date are required for custom period")

        if self.end_date < self.start_date:
            raise ValueError("end_date cannot be earlier than start_date")

        return self
