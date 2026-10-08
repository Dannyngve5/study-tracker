"""rename subsubject to sub_subject

Revision ID: 883a46bb6160
Revises: 2b2d8e032d73
Create Date: 2026-10-07 10:53:21.146426

"""

from collections.abc import Sequence

from alembic import op

revision: str = "883a46bb6160"
down_revision: str | Sequence[str] | None = "2b2d8e032d73"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.rename_table(
        "subsubjects",
        "sub_subjects",
    )

    op.alter_column(
        "study_sessions",
        "subsubject_id",
        new_column_name="sub_subject_id",
    )


def downgrade() -> None:
    op.alter_column(
        "study_sessions",
        "sub_subject_id",
        new_column_name="subsubject_id",
    )

    op.rename_table(
        "sub_subjects",
        "subsubjects",
    )
