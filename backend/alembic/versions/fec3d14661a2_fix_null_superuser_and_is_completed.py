"""fix_null_superuser_and_is_completed

Revision ID: fec3d14661a2
Revises: 8ff8fca3b20a
Create Date: 2026-02-10 14:30:18.822329

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fec3d14661a2'
down_revision: Union[str, None] = '8ff8fca3b20a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Fix users table
    op.execute("UPDATE users SET is_superuser = false WHERE is_superuser IS NULL")
    op.alter_column('users', 'is_superuser',
               existing_type=sa.Boolean(),
               nullable=False)
    
    # Also ensure is_active is not null (though likely already fine)
    op.execute("UPDATE users SET is_active = true WHERE is_active IS NULL")
    op.alter_column('users', 'is_active',
               existing_type=sa.Boolean(),
               nullable=False)

    # Fix week_progress table
    op.execute("UPDATE week_progress SET is_completed = false WHERE is_completed IS NULL")
    op.alter_column('week_progress', 'is_completed',
               existing_type=sa.Boolean(),
               nullable=False)


def downgrade() -> None:
    op.alter_column('week_progress', 'is_completed',
               existing_type=sa.Boolean(),
               nullable=True)
    op.alter_column('users', 'is_active',
               existing_type=sa.Boolean(),
               nullable=True)
    op.alter_column('users', 'is_superuser',
               existing_type=sa.Boolean(),
               nullable=True)