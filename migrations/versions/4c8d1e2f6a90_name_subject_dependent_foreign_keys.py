"""Name foreign keys that prevent deleting a subject with dependents.

Revision ID: 4c8d1e2f6a90
Revises: ef0a1b2c3d4e
Create Date: 2026-10-06
"""

from collections.abc import Sequence

from alembic import op

revision: str = "4c8d1e2f6a90"
down_revision: str | Sequence[str] | None = "ef0a1b2c3d4e"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE subsubjects "
        "RENAME CONSTRAINT subsubjects_subject_id_fkey "
        "TO fk_subsubjects_subject_id_subjects"
    )
    op.execute(
        "ALTER TABLE study_sessions "
        "RENAME CONSTRAINT study_sessions_subject_id_fkey "
        "TO fk_study_sessions_subject_id_subjects"
    )


def downgrade() -> None:
    op.execute(
        "ALTER TABLE study_sessions "
        "RENAME CONSTRAINT fk_study_sessions_subject_id_subjects "
        "TO study_sessions_subject_id_fkey"
    )
    op.execute(
        "ALTER TABLE subsubjects "
        "RENAME CONSTRAINT fk_subsubjects_subject_id_subjects "
        "TO subsubjects_subject_id_fkey"
    )
