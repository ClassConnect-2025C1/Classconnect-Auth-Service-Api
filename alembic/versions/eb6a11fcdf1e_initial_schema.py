"""Initial schema

Revision ID: eb6a11fcdf1e
Revises: 
Create Date: 2025-04-17 09:26:12.232309

"""
from datetime import datetime, timezone
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision: str = 'eb6a11fcdf1e'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create credentials table
    op.create_table(
        'credentials',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(), unique=True, index=True, nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('failed_attempts', sa.Integer(), default=0),
        sa.Column('last_failed_login', sa.DateTime(), nullable=True),
        sa.Column('is_locked', sa.Boolean(), default=False),
        sa.Column('lock_until', sa.DateTime(), nullable=True),
        sa.Column('is_verified', sa.Boolean(), default=False)
    )

    # Create verification_pins table
    op.create_table(
        'verification_pins',
        sa.Column('user_id', sa.String(), primary_key=True),
        sa.Column('pin', sa.String(), nullable=False),
        # Use server_default for consistent timestamp generation
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('is_valid', sa.Boolean(), default=True)
    )

def downgrade() -> None:
    """Downgrade schema."""
    # Drop tables in downgrade
    op.drop_table('verification_pins')
    op.drop_table('credentials')