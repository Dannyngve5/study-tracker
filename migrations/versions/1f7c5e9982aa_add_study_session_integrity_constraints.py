"""add study session integrity constraints

Revision ID: 1f7c5e9982aa
Revises: 883a46bb6160
Create Date: 2026-10-07 14:11:22.002192

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "1f7c5e9982aa"
down_revision: str | Sequence[str] | None = "883a46bb6160"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_check_constraint(
        "ck_study_sessions_duration_non_negative",
        "study_sessions",
        "duration_seconds IS NULL OR duration_seconds >= 0",
    )

    op.create_check_constraint(
        "ck_study_sessions_paused_duration_non_negative",
        "study_sessions",
        "paused_duration_seconds >= 0",
    )

    op.create_check_constraint(
        "ck_study_sessions_finished_ended_at",
        "study_sessions",
        "(status = 'finished' AND ended_at IS NOT NULL) "
        "OR (status <> 'finished' AND ended_at IS NULL)",
    )

    op.create_check_constraint(
        "ck_study_sessions_finished_duration",
        "study_sessions",
        "(status = 'finished' AND duration_seconds IS NOT NULL) "
        "OR (status <> 'finished')",
    )

    op.create_check_constraint(
        "ck_study_sessions_paused_at",
        "study_sessions",
        "(status = 'paused' AND paused_at IS NOT NULL) "
        "OR (status <> 'paused' AND paused_at IS NULL)",
    )


def downgrade() -> None:
    op.drop_constraint(
        "ck_study_sessions_paused_at",
        "study_sessions",
        type_="check",
    )

    op.drop_constraint(
        "ck_study_sessions_finished_duration",
        "study_sessions",
        type_="check",
    )

    op.drop_constraint(
        "ck_study_sessions_finished_ended_at",
        "study_sessions",
        type_="check",
    )

    op.drop_constraint(
        "ck_study_sessions_paused_duration_non_negative",
        "study_sessions",
        type_="check",
    )

    op.drop_constraint(
        "ck_study_sessions_duration_non_negative",
        "study_sessions",
        type_="check",
    )
