"""change metric col name

Revision ID: 2e5f07f81c6c
Revises: cd2dee2a8e58
Create Date: 2021-03-27 19:00:14.793473

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2e5f07f81c6c'
down_revision = 'cd2dee2a8e58'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index(op.f('ix_company_financial_data_calendar_date'), 'company_financial_data', ['calendar_date'], unique=False)
    op.create_index(op.f('ix_company_financial_data_company_id'), 'company_financial_data', ['company_id'], unique=False)
    op.create_index(op.f('ix_company_financial_data_date_filed'), 'company_financial_data', ['date_filed'], unique=False)
    op.drop_index('ix_company_quarterly_financial_data_calendar_date', table_name='company_financial_data')
    op.drop_index('ix_company_quarterly_financial_data_company_id', table_name='company_financial_data')
    op.drop_index('ix_company_quarterly_financial_data_date_filed', table_name='company_financial_data')
    op.add_column('company_metric', sa.Column('company_business_or_product_id', sa.Integer(), nullable=False))
    op.create_index(op.f('ix_company_metric_company_business_or_product_id'), 'company_metric', ['company_business_or_product_id'], unique=False)
    op.drop_index('ix_company_metric_company_business_or_product', table_name='company_metric')
    op.drop_constraint('fk_company_metric_company_business_or_product_company_b_e2d3', 'company_metric', type_='foreignkey')
    op.create_foreign_key(op.f('fk_company_metric_company_business_or_product_id_company_business_or_product'), 'company_metric', 'company_business_or_product', ['company_business_or_product_id'], ['id'], onupdate='CASCADE', ondelete='CASCADE')
    op.drop_column('company_metric', 'company_business_or_product')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('company_metric', sa.Column('company_business_or_product', sa.INTEGER(), autoincrement=False, nullable=False))
    op.drop_constraint(op.f('fk_company_metric_company_business_or_product_id_company_business_or_product'), 'company_metric', type_='foreignkey')
    op.create_foreign_key('fk_company_metric_company_business_or_product_company_b_e2d3', 'company_metric', 'company_business_or_product', ['company_business_or_product'], ['id'], onupdate='CASCADE', ondelete='CASCADE')
    op.create_index('ix_company_metric_company_business_or_product', 'company_metric', ['company_business_or_product'], unique=False)
    op.drop_index(op.f('ix_company_metric_company_business_or_product_id'), table_name='company_metric')
    op.drop_column('company_metric', 'company_business_or_product_id')
    op.create_index('ix_company_quarterly_financial_data_date_filed', 'company_financial_data', ['date_filed'], unique=False)
    op.create_index('ix_company_quarterly_financial_data_company_id', 'company_financial_data', ['company_id'], unique=False)
    op.create_index('ix_company_quarterly_financial_data_calendar_date', 'company_financial_data', ['calendar_date'], unique=False)
    op.drop_index(op.f('ix_company_financial_data_date_filed'), table_name='company_financial_data')
    op.drop_index(op.f('ix_company_financial_data_company_id'), table_name='company_financial_data')
    op.drop_index(op.f('ix_company_financial_data_calendar_date'), table_name='company_financial_data')
    # ### end Alembic commands ###
