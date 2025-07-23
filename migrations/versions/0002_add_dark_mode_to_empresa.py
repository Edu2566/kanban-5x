"""Add dark_mode to Empresa

Revision ID: 0002
Revises: 0001
Create Date: 2024-01-01 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('empresas', sa.Column('dark_mode', sa.Boolean(), nullable=False, server_default=sa.text('0')))
    op.alter_column('empresas', 'dark_mode', server_default=None)


def downgrade():
    op.drop_column('empresas', 'dark_mode')

