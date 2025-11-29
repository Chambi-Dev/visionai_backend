"""make_user_id_nullable_in_predictions_log

Revision ID: bbe293e60950
Revises: 112ffe1aebec
Create Date: 2025-11-29 16:52:45.589506

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bbe293e60950'
down_revision: Union[str, Sequence[str], None] = '112ffe1aebec'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Hacer user_id nullable para permitir predicciones sin autenticación
    op.alter_column('predictions_log', 'user_id',
                    existing_type=sa.Integer(),
                    nullable=True)


def downgrade() -> None:
    """Downgrade schema."""
    # Revertir a NOT NULL
    op.alter_column('predictions_log', 'user_id',
                    existing_type=sa.Integer(),
                    nullable=False)
