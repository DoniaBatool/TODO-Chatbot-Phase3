"""Add conversation state tracking fields

Revision ID: 3b7378ec255f
Revises: 6ec79efb1d8a
Create Date: 2026-01-28 07:40:34.422798

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '3b7378ec255f'
down_revision: Union[str, Sequence[str], None] = '6ec79efb1d8a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - Add conversation state tracking fields."""
    # Add new columns to conversations table
    op.add_column(
        'conversations',
        sa.Column('current_intent', sa.String(), nullable=True, server_default='NEUTRAL')
    )
    op.add_column(
        'conversations',
        sa.Column('state_data', postgresql.JSON(astext_type=sa.Text()), nullable=True)
    )
    op.add_column(
        'conversations',
        sa.Column('target_task_id', sa.Integer(), nullable=True)
    )

    # Set default value for existing rows
    op.execute("UPDATE conversations SET current_intent = 'NEUTRAL' WHERE current_intent IS NULL")

    # Make current_intent non-nullable after setting defaults
    op.alter_column('conversations', 'current_intent', nullable=False)


def downgrade() -> None:
    """Downgrade schema - Remove conversation state tracking fields."""
    # Remove columns in reverse order
    op.drop_column('conversations', 'target_task_id')
    op.drop_column('conversations', 'state_data')
    op.drop_column('conversations', 'current_intent')
