<%text>#
Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}
</%text>

from alembic import op
import sqlalchemy as sa


def upgrade():
${upgrades if upgrades else '    pass'}


def downgrade():
${downgrades if downgrades else '    pass'}
