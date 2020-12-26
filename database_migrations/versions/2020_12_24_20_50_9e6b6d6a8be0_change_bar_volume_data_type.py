"""Change bar volume data type

Revision ID: 9e6b6d6a8be0
Revises: bcc76ce93a8e
Create Date: 2020-12-24 20:50:58.017394

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9e6b6d6a8be0'
down_revision = 'bcc76ce93a8e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('bar_data', 'bar_volume',
               existing_type=sa.NUMERIC(),
               type_=sa.BigInteger(),
               existing_nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('bar_data', 'bar_volume',
               existing_type=sa.BigInteger(),
               type_=sa.NUMERIC(),
               existing_nullable=True)
    # ### end Alembic commands ###
