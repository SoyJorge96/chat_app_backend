"""creando tablas iniciales

Revision ID: a791ea448eb1
Revises: 65299f27b947
Create Date: 2026-05-06 23:32:20.460140

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a791ea448eb1'
down_revision: Union[str, Sequence[str], None] = '65299f27b947'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
