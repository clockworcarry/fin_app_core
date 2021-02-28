"""Metrics, cpny. summary and cpy. dev tables

Revision ID: 15e45917f5ab
Revises: 16f6aeb9ee5e
Create Date: 2021-02-22 20:29:20.011653

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
revision = '15e45917f5ab'
down_revision = '16f6aeb9ee5e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('company_development',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('company_id', sa.Integer(), nullable=False),
    sa.Column('display_name', sa.String(length=120), nullable=False),
    sa.Column('dev_type', sa.SmallInteger(), nullable=False),
    sa.Column('data_type', sa.SmallInteger(), nullable=False),
    sa.Column('data', sa.LargeBinary(), nullable=True),
    sa.Column('date_recorded', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['company_id'], ['company.id'], name=op.f('fk_company_development_company_id_company'), onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_company_development'))
    )
    op.create_index(op.f('ix_company_development_company_id'), 'company_development', ['company_id'], unique=False)
    op.create_index(op.f('ix_company_development_data_type'), 'company_development', ['data_type'], unique=False)
    op.create_index(op.f('ix_company_development_date_recorded'), 'company_development', ['date_recorded'], unique=False)
    op.create_index(op.f('ix_company_development_dev_type'), 'company_development', ['dev_type'], unique=False)
    op.create_table('company_metric',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('company_id', sa.Integer(), nullable=False),
    sa.Column('code', sa.String(length=60), nullable=False),
    sa.Column('display_name', sa.String(length=120), nullable=False),
    sa.Column('metric_type', sa.SmallInteger(), nullable=False),
    sa.Column('date_recorded', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['company_id'], ['company.id'], name=op.f('fk_company_metric_company_id_company'), onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_company_metric'))
    )
    op.create_index(op.f('ix_company_metric_code'), 'company_metric', ['code'], unique=False)
    op.create_index(op.f('ix_company_metric_company_id'), 'company_metric', ['company_id'], unique=False)
    op.create_index(op.f('ix_company_metric_date_recorded'), 'company_metric', ['date_recorded'], unique=False)
    op.create_index(op.f('ix_company_metric_metric_type'), 'company_metric', ['metric_type'], unique=False)
    op.create_table('company_summary',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('company_id', sa.Integer(), nullable=False),
    sa.Column('data', sa.LargeBinary(), nullable=True),
    sa.Column('update_stamp', sa.DateTime(timezone=True), server_default=FetchedValue(), nullable=False),
    sa.ForeignKeyConstraint(['company_id'], ['company.id'], name=op.f('fk_company_summary_company_id_company'), onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_company_summary'))
    )
    op.create_index(op.f('ix_company_summary_company_id'), 'company_summary', ['company_id'], unique=False)
    op.create_index(op.f('ix_company_summary_update_stamp'), 'company_summary', ['update_stamp'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_company_summary_update_stamp'), table_name='company_summary')
    op.drop_index(op.f('ix_company_summary_company_id'), table_name='company_summary')
    op.drop_table('company_summary')
    op.drop_index(op.f('ix_company_metric_metric_type'), table_name='company_metric')
    op.drop_index(op.f('ix_company_metric_date_recorded'), table_name='company_metric')
    op.drop_index(op.f('ix_company_metric_company_id'), table_name='company_metric')
    op.drop_index(op.f('ix_company_metric_code'), table_name='company_metric')
    op.drop_table('company_metric')
    op.drop_index(op.f('ix_company_development_dev_type'), table_name='company_development')
    op.drop_index(op.f('ix_company_development_date_recorded'), table_name='company_development')
    op.drop_index(op.f('ix_company_development_data_type'), table_name='company_development')
    op.drop_index(op.f('ix_company_development_company_id'), table_name='company_development')
    op.drop_table('company_development')
    # ### end Alembic commands ###