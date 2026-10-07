"""add study session state

Revision ID: 2b2d8e032d73
Revises: 4c8d1e2f6a90
Create Date: 2026-10-07 10:09:36.852883

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "2b2d8e032d73"
down_revision: Union[str, Sequence[str], None] = "4c8d1e2f6a90"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    study_session_status = sa.Enum(
        "running",
        "paused",
        "finished",
        name="studysessionstatus",
    )

    study_session_status.create(op.get_bind())

    op.add_column(
        "study_sessions",
        sa.Column(
            "status",
            study_session_status,
            nullable=False,
        ),
    )

    op.add_column(
        "study_sessions",
        sa.Column(
            "paused_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )

    op.add_column(
        "study_sessions",
        sa.Column(
            "paused_duration_seconds",
            sa.Integer(),
            nullable=False,
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_column(
        "study_sessions",
        "paused_duration_seconds",
    )

    op.drop_column(
        "study_sessions",
        "paused_at",
    )

    op.drop_column(
        "study_sessions",
        "status",
    )

    study_session_status = sa.Enum(
        "running",
        "paused",
        "finished",
        name="studysessionstatus",
    )

    study_session_status.drop(op.get_bind())
