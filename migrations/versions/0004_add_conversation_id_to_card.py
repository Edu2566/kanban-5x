"""Add conversation_id to Card

Revision ID: 0004
Revises: 0003
Create Date: 2024-01-01 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('cards', sa.Column('conversation_id', sa.String(), nullable=True))


def downgrade():
    op.drop_column('cards', 'conversation_id')
