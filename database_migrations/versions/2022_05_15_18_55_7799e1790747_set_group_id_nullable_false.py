"""set group_id nullable false

Revision ID: 7799e1790747
Revises: 28c1b60ddc31
Create Date: 2022-05-15 18:55:36.217892

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7799e1790747'
down_revision = '28c1b60ddc31'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('company_sector_relation', 'group_id',
               nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('company_sector_relation', 'group_id',
               nullable=True)
    # ### end Alembic commands ###