"""Add color to Column

Revision ID: 0005
Revises: 0004
Create Date: 2024-01-01 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('columns', sa.Column('color', sa.String(length=7), nullable=True))


def downgrade():
    op.drop_column('columns', 'color')
