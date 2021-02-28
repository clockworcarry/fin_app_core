"""lookback nullable false

Revision ID: 2d9062f37c08
Revises: d9d039f772c9
Create Date: 2021-02-26 11:08:10.239263

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2d9062f37c08'
down_revision = 'd9d039f772c9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('company_metric', 'look_back',
               existing_type=sa.SMALLINT(),
               nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('company_metric', 'look_back',
               existing_type=sa.SMALLINT(),
               nullable=True)
    # ### end Alembic commands ###
