"""change_user_to_user_id_in_predictions_log

Revision ID: 112ffe1aebec
Revises: a8ae8804d8b9
Create Date: 2025-11-29 16:35:29.338219

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '112ffe1aebec'
down_revision: Union[str, Sequence[str], None] = 'a8ae8804d8b9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Eliminar la columna 'user' de tipo String
    op.drop_column('predictions_log', 'user')
    
    # Agregar la nueva columna 'user_id' de tipo Integer con foreign key
    op.add_column(
        'predictions_log',
        sa.Column('user_id', sa.Integer(), nullable=False)
    )
    
    # Crear la foreign key constraint
    op.create_foreign_key(
        'fk_predictions_log_user_id',
        'predictions_log',
        'users',
        ['user_id'],
        ['user_id']
    )
    
    # Cambiar los tipos de las columnas emotion_id y model_id de Integer a BigInteger
    op.alter_column('predictions_log', 'emotion_id',
                    existing_type=sa.Integer(),
                    type_=sa.BigInteger(),
                    nullable=False)
    
    op.alter_column('predictions_log', 'model_id',
                    existing_type=sa.Integer(),
                    type_=sa.BigInteger(),
                    nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Cambiar los tipos de vuelta a Integer
    op.alter_column('predictions_log', 'emotion_id',
                    existing_type=sa.BigInteger(),
                    type_=sa.Integer(),
                    nullable=False)
    
    op.alter_column('predictions_log', 'model_id',
                    existing_type=sa.BigInteger(),
                    type_=sa.Integer(),
                    nullable=False)
    
    # Eliminar la foreign key constraint
    op.drop_constraint('fk_predictions_log_user_id', 'predictions_log', type_='foreignkey')
    
    # Eliminar la columna user_id
    op.drop_column('predictions_log', 'user_id')
    
    # Agregar de vuelta la columna user de tipo String
    op.add_column(
        'predictions_log',
        sa.Column('user', sa.String(50), nullable=True)
    )
