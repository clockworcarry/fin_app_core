"""added locked cols to fundamental data tables

Revision ID: 8d3c7b192a5e
Revises: 330de9b51b50
Create Date: 2020-12-12 12:15:54.823772

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8d3c7b192a5e'
down_revision = '330de9b51b50'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('balance_sheet_data', sa.Column('locked', sa.Boolean(), server_default=sa.text('false'), nullable=False))
    op.add_column('cash_flow_statement_data', sa.Column('locked', sa.Boolean(), server_default=sa.text('false'), nullable=False))
    op.add_column('income_statement_data', sa.Column('locked', sa.Boolean(), server_default=sa.text('false'), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('income_statement_data', 'locked')
    op.drop_column('cash_flow_statement_data', 'locked')
    op.drop_column('balance_sheet_data', 'locked')
    # ### end Alembic commands ###