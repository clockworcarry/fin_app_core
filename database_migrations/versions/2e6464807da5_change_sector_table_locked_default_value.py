"""Change sector table locked default value

Revision ID: 2e6464807da5
Revises: 6c8a00b6ac3b
Create Date: 2020-11-10 20:40:38.298831

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2e6464807da5'
down_revision = '6c8a00b6ac3b'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(table_name="sector", column_name="locked", server_default="False")


def downgrade():
    op.alter_column(table_name="sector", column_name="locked", server_default="True")
