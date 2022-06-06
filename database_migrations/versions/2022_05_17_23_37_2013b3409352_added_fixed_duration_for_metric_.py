"""added fixed duration for metric descriptions

Revision ID: 2013b3409352
Revises: 5bf43a9fe9c5
Create Date: 2022-05-17 23:37:15.225599

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2013b3409352'
down_revision = '5bf43a9fe9c5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_company_metric_date_recorded', table_name='company_metric')
    op.drop_column('company_metric', 'date_recorded')
    op.add_column('company_metric_description', sa.Column('metric_fixed_quarter', sa.SmallInteger(), nullable=True))
    op.add_column('company_metric_description', sa.Column('metric_fixed_year', sa.SmallInteger(), nullable=True))
    op.add_column('company_metric_description', sa.Column('quarter_recorded', sa.SmallInteger(), nullable=True))
    op.add_column('company_metric_description', sa.Column('year_recorded', sa.SmallInteger(), nullable=True))
    op.alter_column('company_metric_description', 'metric_duration',
               existing_type=sa.SMALLINT(),
               nullable=True)
    op.create_index(op.f('ix_company_metric_description_metric_fixed_quarter'), 'company_metric_description', ['metric_fixed_quarter'], unique=False)
    op.create_index(op.f('ix_company_metric_description_metric_fixed_year'), 'company_metric_description', ['metric_fixed_year'], unique=False)
    op.create_index(op.f('ix_company_metric_description_quarter_recorded'), 'company_metric_description', ['quarter_recorded'], unique=False)
    op.create_index(op.f('ix_company_metric_description_year_recorded'), 'company_metric_description', ['year_recorded'], unique=False)
    op.drop_constraint('uq_company_metric_description_code', 'company_metric_description', type_='unique')
    op.create_unique_constraint(op.f('uq_company_metric_description_code'), 'company_metric_description', ['code', 'metric_data_type', 'metric_duration', 'metric_duration_type', 'look_back', 'metric_fixed_year', 'metric_fixed_quarter'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(op.f('uq_company_metric_description_code'), 'company_metric_description', type_='unique')
    op.create_unique_constraint('uq_company_metric_description_code', 'company_metric_description', ['code', 'metric_data_type', 'metric_duration', 'metric_duration_type', 'look_back'])
    op.drop_index(op.f('ix_company_metric_description_year_recorded'), table_name='company_metric_description')
    op.drop_index(op.f('ix_company_metric_description_quarter_recorded'), table_name='company_metric_description')
    op.drop_index(op.f('ix_company_metric_description_metric_fixed_year'), table_name='company_metric_description')
    op.drop_index(op.f('ix_company_metric_description_metric_fixed_quarter'), table_name='company_metric_description')
    op.alter_column('company_metric_description', 'metric_duration',
               existing_type=sa.SMALLINT(),
               nullable=False)
    op.drop_column('company_metric_description', 'year_recorded')
    op.drop_column('company_metric_description', 'quarter_recorded')
    op.drop_column('company_metric_description', 'metric_fixed_year')
    op.drop_column('company_metric_description', 'metric_fixed_quarter')
    op.add_column('company_metric', sa.Column('date_recorded', sa.DATE(), autoincrement=False, nullable=False))
    op.create_index('ix_company_metric_date_recorded', 'company_metric', ['date_recorded'], unique=False)
    # ### end Alembic commands ###
