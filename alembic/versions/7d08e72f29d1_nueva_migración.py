from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, String, Integer, Boolean, DateTime
from datetime import datetime

# revision identifiers, used by Alembic.
revision: str = '7d08e72f29d1'
down_revision: Union[str, None] = '30078989d76b'
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
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, default=datetime.utcnow),
        sa.Column('is_valid', sa.Boolean(), default=True)
    )

def downgrade() -> None:
    """Downgrade schema."""
    # Drop tables in downgrade
    op.drop_table('credentials')
    op.drop_table('verification_pins')
