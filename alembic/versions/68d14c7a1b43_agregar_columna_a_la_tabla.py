"""Agregar columna a la tabla

Revision ID: 68d14c7a1b43
Revises: 66020a42956b
Create Date: 2025-04-15 00:00:08.401931

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '68d14c7a1b43'
down_revision: Union[str, None] = '9e86a2b7e8c2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('credentials', sa.Column(
        'is_verified',
        sa.Boolean(),
        server_default=sa.text('false'),
        nullable=False  # o False si querés que siempre tenga un valor
    ))
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('credentials', 'is_verified')
    # ### end Alembic commands ###
