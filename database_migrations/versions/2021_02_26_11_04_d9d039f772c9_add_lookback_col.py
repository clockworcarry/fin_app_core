"""add lookback col

Revision ID: d9d039f772c9
Revises: 39e5169fe00c
Create Date: 2021-02-26 11:04:31.375294

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd9d039f772c9'
down_revision = '39e5169fe00c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('company_metric', sa.Column('look_back', sa.SmallInteger(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('company_metric', 'look_back')
    # ### end Alembic commands ###
