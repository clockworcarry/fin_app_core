"""name_code country table

Revision ID: e8518960f8d2
Revises: feb54d11c85f
Create Date: 2020-11-22 20:32:25.090045

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e8518960f8d2'
down_revision = 'feb54d11c85f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('country_info', 'name_code',
               existing_type=sa.VARCHAR(length=10),
               nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('country_info', 'name_code',
               existing_type=sa.VARCHAR(length=10),
               nullable=True)
    # ### end Alembic commands ###
