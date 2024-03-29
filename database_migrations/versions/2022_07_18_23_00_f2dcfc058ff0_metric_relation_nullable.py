"""metric relation nullable

Revision ID: f2dcfc058ff0
Revises: 2013b3409352
Create Date: 2022-07-18 23:00:44.481012

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f2dcfc058ff0'
down_revision = '2013b3409352'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('company_metric_description', 'metric_duration',
               existing_type=sa.SMALLINT(),
               nullable=False)
    op.alter_column('company_metric_description', 'metric_fixed_quarter',
               existing_type=sa.SMALLINT(),
               nullable=False)
    op.alter_column('company_metric_description', 'metric_fixed_year',
               existing_type=sa.SMALLINT(),
               nullable=False)
    op.alter_column('company_metric_description', 'quarter_recorded',
               existing_type=sa.SMALLINT(),
               nullable=False)
    op.alter_column('company_metric_description', 'year_recorded',
               existing_type=sa.SMALLINT(),
               nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('company_metric_description', 'year_recorded',
               existing_type=sa.SMALLINT(),
               nullable=True)
    op.alter_column('company_metric_description', 'quarter_recorded',
               existing_type=sa.SMALLINT(),
               nullable=True)
    op.alter_column('company_metric_description', 'metric_fixed_year',
               existing_type=sa.SMALLINT(),
               nullable=True)
    op.alter_column('company_metric_description', 'metric_fixed_quarter',
               existing_type=sa.SMALLINT(),
               nullable=True)
    op.alter_column('company_metric_description', 'metric_duration',
               existing_type=sa.SMALLINT(),
               nullable=True)
    # ### end Alembic commands ###
