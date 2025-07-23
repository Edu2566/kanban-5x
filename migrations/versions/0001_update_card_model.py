"""Update Card model

Revision ID: 0001
Revises: 
Create Date: 2024-01-01 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('cards', sa.Column('valor_negociado', sa.Float(), nullable=True))
    op.alter_column('cards', 'usuario_id', new_column_name='vendedor_id')
    op.create_foreign_key(None, 'cards', 'usuarios', ['vendedor_id'], ['id'])
    op.drop_column('cards', 'description')


def downgrade():
    op.add_column('cards', sa.Column('description', sa.String(length=300), nullable=True))
    op.drop_constraint(None, 'cards', type_='foreignkey')
    op.alter_column('cards', 'vendedor_id', new_column_name='usuario_id')
    op.drop_column('cards', 'valor_negociado')
