"""add brokerage column trade tbl

Revision ID: e589d37c7b8b
Revises: 126654ba690f
Create Date: 2021-04-12 23:55:15.891012

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e589d37c7b8b'
down_revision = '126654ba690f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('account_trade', sa.Column('brokerage_id', sa.SmallInteger(), nullable=False))
    op.create_index(op.f('ix_account_trade_brokerage_id'), 'account_trade', ['brokerage_id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_account_trade_brokerage_id'), table_name='account_trade')
    op.drop_column('account_trade', 'brokerage_id')
    # ### end Alembic commands ###
