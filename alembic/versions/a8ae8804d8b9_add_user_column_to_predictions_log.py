"""add_user_column_to_predictions_log

Revision ID: a8ae8804d8b9
Revises: 79fc21215224
Create Date: 2025-11-28 17:37:22.738941

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a8ae8804d8b9'
down_revision: Union[str, Sequence[str], None] = '79fc21215224'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Agregar columna user a predictions_log (nullable para datos existentes)
    op.add_column(
        'predictions_log',
        sa.Column('user', sa.String(50), nullable=True)
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Eliminar columna user de predictions_log
    op.drop_column('predictions_log', 'user')
