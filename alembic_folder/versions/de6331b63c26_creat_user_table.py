"""creat user table

Revision ID: de6331b63c26
Revises: 5e410cbebfaf
Create Date: 2026-10-18 13:24:31.704492

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'de6331b63c26'
down_revision: Union[str, Sequence[str], None] = '5e410cbebfaf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.Integer, nullable=False),
        sa.Column('email', sa.String, nullable=False, unique=True),
        sa.Column('password', sa.String, nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),sa.PrimaryKeyConstraint('id'))
    pass


def downgrade() -> None:
    op.drop_table('users')
    pass
