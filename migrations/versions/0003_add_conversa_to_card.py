"""Add conversa field to Card

Revision ID: 0003
Revises: 0002
Create Date: 2024-01-01 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('cards', sa.Column('conversa', sa.String(), nullable=True))


def downgrade():
    op.drop_column('cards', 'conversa')
