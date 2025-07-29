"""Add created_at to Card

Revision ID: 0008
Revises: 0007
Create Date: 2024-01-01 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('cards', sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('(CURRENT_TIMESTAMP)')))
    op.alter_column('cards', 'created_at', server_default=None)


def downgrade():
    op.drop_column('cards', 'created_at')
