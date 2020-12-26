"""add company_misc_info tbl and remove col from company tbl

Revision ID: 451d94b90fdd
Revises: 8d3c7b192a5e
Create Date: 2020-12-12 21:21:50.639732

"""
from alembic import op
import sqlalchemy as sa
from alembic import op
from sqlalchemy import *
from sqlalchemy import orm
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import *
from sqlalchemy.schema import *


# revision identifiers, used by Alembic.
revision = '451d94b90fdd'
down_revision = '8d3c7b192a5e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('company_misc_info',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('company_id', sa.Integer(), nullable=False),
    sa.Column('shares_bas', sa.BigInteger(), nullable=True),
    sa.Column('shares_dil', sa.BigInteger(), nullable=True),
    sa.Column('date_recorded', sa.DateTime(timezone=True), nullable=False),
    sa.Column('locked', sa.Boolean(), server_default=sa.text('false'), nullable=False),
    sa.Column('update_stamp', sa.DateTime(timezone=True), server_default=FetchedValue(), nullable=False),
    sa.ForeignKeyConstraint(['company_id'], ['company.id'], name=op.f('fk_company_misc_info_company_id_company'), onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_company_misc_info'))
    )
    op.drop_column('company', 'shares_basic')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('company', sa.Column('shares_basic', sa.BIGINT(), autoincrement=False, nullable=True))
    op.drop_table('company_misc_info')
    # ### end Alembic commands ###