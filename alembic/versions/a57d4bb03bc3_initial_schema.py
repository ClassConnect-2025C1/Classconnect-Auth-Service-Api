"""initial schema

Revision ID: a57d4bb03bc3
Revises: 
Create Date: 2025-04-16 10:54:25.070180

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a57d4bb03bc3'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'user_profiles',
        sa.Column('id', sa.UUID(), autoincrement=False, nullable=False),
        sa.Column('email', sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column('last_name', sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column('location', sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column('role', sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column('photo', postgresql.BYTEA(), autoincrement=False, nullable=True),
        sa.Column('bio', sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.PrimaryKeyConstraint('id', name='user_profiles_pkey'),
        sa.UniqueConstraint('email', name='user_profiles_email_key')
    )


def downgrade() -> None:
    """Downgrade schema."""
    pass
