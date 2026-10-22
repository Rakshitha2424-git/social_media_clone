"""add post media table

Revision ID: f742da932b10
Revises: b00345e42359
Create Date: 2026-10-22

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f742da932b10"
down_revision: Union[str, Sequence[str], None] = "b00345e42359"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "post_media",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("post_id", sa.Integer(), nullable=False),
        sa.Column("stored_name", sa.String(), nullable=False),
        sa.Column("media_type", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(["post_id"], ["posts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("stored_name"),
    )


def downgrade() -> None:
    op.drop_table("post_media")
