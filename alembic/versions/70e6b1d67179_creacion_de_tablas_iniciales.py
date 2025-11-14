"""Creacion de tablas iniciales

Revision ID: 70e6b1d67179
Revises: 
Create Date: 2025-11-06 21:58:23.205001

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '70e6b1d67179'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Crear tabla emotion_class
    op.create_table(
        'emotion_class',
        sa.Column('emotion_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('emotion_name', sa.String(length=50), nullable=False),
        sa.Column('emotion_desc', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('emotion_id'),
        sa.UniqueConstraint('emotion_name')
    )
    
    # Crear tabla model_version
    op.create_table(
        'model_version',
        sa.Column('model_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('model_version_tag', sa.String(length=100), nullable=False),
        sa.Column('model_filename', sa.String(length=255), nullable=False),
        sa.Column('model_status', sa.String(length=2), nullable=False),
        sa.Column('creation_date', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('model_id'),
        sa.UniqueConstraint('model_version_tag')
    )
    
    # Crear tabla predictions_log
    op.create_table(
        'predictions_log',
        sa.Column('predic_id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('emotion_id', sa.Integer(), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('model_id', sa.Integer(), nullable=False),
        sa.Column('processing_time_ms', sa.Integer(), nullable=True),
        sa.Column('source_ip', postgresql.INET(), nullable=True),
        sa.Column('timestamp', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['emotion_id'], ['emotion_class.emotion_id'], ),
        sa.ForeignKeyConstraint(['model_id'], ['model_version.model_id'], ),
        sa.PrimaryKeyConstraint('predic_id')
    )
    
    # Insertar datos iniciales de emociones
    op.execute("""
        INSERT INTO emotion_class (emotion_name, emotion_desc) VALUES
        ('angry', 'Enojo o ira'),
        ('disgust', 'Disgusto o asco'),
        ('fear', 'Miedo o temor'),
        ('happy', 'Felicidad o alegría'),
        ('neutral', 'Neutral o sin emoción aparente'),
        ('sad', 'Tristeza'),
        ('surprise', 'Sorpresa')
    """)
    
    # Insertar versión inicial del modelo
    op.execute("""
        INSERT INTO model_version (model_version_tag, model_filename, model_status)
        VALUES ('v1.0.0', 'modelo_emociones.h5', '01')
    """)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('predictions_log')
    op.drop_table('model_version')
    op.drop_table('emotion_class')

