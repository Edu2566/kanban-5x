"""Add Panel model and panel_users table

Revision ID: 0006
Revises: 0005
Create Date: 2024-01-01 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'panels',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(length=80), nullable=False),
        sa.Column('empresa_id', sa.Integer(), nullable=False),
    )
    op.create_foreign_key(None, 'panels', 'empresas', ['empresa_id'], ['id'])

    op.create_table(
        'panel_users',
        sa.Column('panel_id', sa.Integer(), nullable=False),
        sa.Column('usuario_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['panel_id'], ['panels.id']),
        sa.ForeignKeyConstraint(['usuario_id'], ['usuarios.id']),
        sa.PrimaryKeyConstraint('panel_id', 'usuario_id'),
    )

    op.add_column('columns', sa.Column('panel_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'columns', 'panels', ['panel_id'], ['id'])

    # create one panel per existing empresa and assign columns
    connection = op.get_bind()
    empresas = connection.execute(sa.text('SELECT id, nome FROM empresas')).fetchall()
    for empresa in empresas:
        res = connection.execute(
            sa.text('INSERT INTO panels (name, empresa_id) VALUES (:name, :eid)'),
            {'name': 'Default', 'eid': empresa.id},
        )
        panel_id = res.lastrowid
        connection.execute(
            sa.text('UPDATE columns SET panel_id = :pid WHERE empresa_id = :eid'),
            {'pid': panel_id, 'eid': empresa.id},
        )


def downgrade():
    op.drop_constraint(None, 'columns', type_='foreignkey')
    op.drop_column('columns', 'panel_id')
    op.drop_table('panel_users')
    op.drop_table('panels')
