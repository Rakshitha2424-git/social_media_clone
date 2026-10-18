"""auto-vote

Revision ID: 75725029dee3
Revises: 7489bd29a583
Create Date: 2026-10-18 13:46:52.803206

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '75725029dee3'
down_revision: Union[str, Sequence[str], None] = '7489bd29a583'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "votes",
        sa.Column("user_id", sa.Integer, nullable=False),
        sa.Column("post_id", sa.Integer, nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["post_id"],
            ["posts.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("user_id", "post_id"),
    )


def downgrade() -> None:
    op.drop_table("votes")