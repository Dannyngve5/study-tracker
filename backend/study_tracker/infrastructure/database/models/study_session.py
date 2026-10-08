from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, func
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column
from study_tracker.domain.enums.study_session_status import StudySessionStatus
from study_tracker.infrastructure.database.base import Base


class StudySession(Base):
    __tablename__ = "study_sessions"

    __table_args__ = (
        CheckConstraint(
            "duration_seconds IS NULL OR duration_seconds >= 0",
            name="ck_study_sessions_duration_non_negative",
        ),
        CheckConstraint(
            "paused_duration_seconds >= 0",
            name="ck_study_sessions_paused_duration_non_negative",
        ),
        CheckConstraint(
            "(status = 'finished' AND ended_at IS NOT NULL)"
            "OR (status <> 'finished' AND ended_at IS NULL)",
            name="ck_study_sessions_finished_ended_at",
        ),
        CheckConstraint(
            "(status = 'finished' AND duration_seconds IS NOT NULL) "
            "OR (status <> 'finished')",
            name="ck_study_sessions_finished_duration",
        ),
        CheckConstraint(
            "(status = 'paused' AND paused_at IS NOT NULL) "
            "OR (status <> 'paused' AND paused_at IS NULL)",
            name="ck_study_sessions_paused_at",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    subject_id: Mapped[int] = mapped_column(
        ForeignKey(
            "subjects.id",
            name="fk_study_sessions_subject_id_subjects",
        ),
        nullable=False,
    )

    sub_subject_id: Mapped[int | None] = mapped_column(
        ForeignKey("sub_subjects.id"),
        nullable=True,
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    ended_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    duration_seconds: Mapped[int | None] = mapped_column(
        nullable=True,
    )

    status: Mapped[StudySessionStatus] = mapped_column(
        SqlEnum(
            StudySessionStatus,
            values_callable=lambda enum: [member.value for member in enum],
        ),
        nullable=False,
    )

    paused_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    paused_duration_seconds: Mapped[int] = mapped_column(
        nullable=False,
        default=0,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
