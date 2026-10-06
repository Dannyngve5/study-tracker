"""Name the unique constraint on subjects.name.

Revision ID: ef0a1b2c3d4e
Revises: 0b92ec62e36e
Create Date: 2026-10-06
"""

from collections.abc import Sequence

from alembic import op

revision: str = "ef0a1b2c3d4e"
down_revision: str | Sequence[str] | None = "0b92ec62e36e"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE subjects "
        "RENAME CONSTRAINT subjects_name_key TO uq_subjects_name"
    )


def downgrade() -> None:
    op.execute(
        "ALTER TABLE subjects "
        "RENAME CONSTRAINT uq_subjects_name TO subjects_name_key"
    )
