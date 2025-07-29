"""Remove empresa_id from Column

Revision ID: 0007
Revises: 0006
Create Date: 2024-01-01 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa


def upgrade():
    op.drop_constraint(None, 'columns', type_='foreignkey')
    op.drop_column('columns', 'empresa_id')


def downgrade():
    op.add_column('columns', sa.Column('empresa_id', sa.Integer(), nullable=False))
    op.create_foreign_key(None, 'columns', 'empresas', ['empresa_id'], ['id'])
