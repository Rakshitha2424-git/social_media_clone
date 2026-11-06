"""add content column

Revision ID: 5e410cbebfaf
Revises: 8bbb102edb68
Create Date: 2026-10-18 13:18:51.229237

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5e410cbebfaf'
down_revision: Union[str, Sequence[str], None] = '8bbb102edb68'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('posts', sa.Column('content', sa.String, nullable=False))
    pass


def downgrade() -> None:
    op.drop_column('posts', 'content')
    pass
