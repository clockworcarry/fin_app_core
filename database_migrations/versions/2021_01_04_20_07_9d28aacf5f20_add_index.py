"""Add index

Revision ID: 9d28aacf5f20
Revises: 9e6b6d6a8be0
Create Date: 2021-01-04 20:07:36.211636

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9d28aacf5f20'
down_revision = '9e6b6d6a8be0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index(op.f('ix_balance_sheet_data_calendar_date'), 'balance_sheet_data', ['calendar_date'], unique=False)
    op.create_index(op.f('ix_balance_sheet_data_company_id'), 'balance_sheet_data', ['company_id'], unique=False)
    op.create_index(op.f('ix_balance_sheet_data_date_filed'), 'balance_sheet_data', ['date_filed'], unique=False)
    op.drop_constraint('uq_bar_data_company_id', 'bar_data', type_='unique')
    op.create_unique_constraint(op.f('uq_bar_data_company_id'), 'bar_data', ['company_id', 'bar_type', 'bar_size', 'bar_date', 'exchange_id'])
    op.create_index(op.f('ix_cash_flow_statement_data_calendar_date'), 'cash_flow_statement_data', ['calendar_date'], unique=False)
    op.create_index(op.f('ix_cash_flow_statement_data_company_id'), 'cash_flow_statement_data', ['company_id'], unique=False)
    op.create_index(op.f('ix_cash_flow_statement_data_date_filed'), 'cash_flow_statement_data', ['date_filed'], unique=False)
    op.create_index(op.f('ix_company_misc_info_company_id'), 'company_misc_info', ['company_id'], unique=False)
    op.create_index(op.f('ix_cron_job_run_log_id'), 'cron_job_run', ['log_id'], unique=False)
    op.create_index(op.f('ix_exchange_country_info_id'), 'exchange', ['country_info_id'], unique=False)
    op.create_index(op.f('ix_income_statement_data_calendar_date'), 'income_statement_data', ['calendar_date'], unique=False)
    op.create_index(op.f('ix_income_statement_data_company_id'), 'income_statement_data', ['company_id'], unique=False)
    op.create_index(op.f('ix_income_statement_data_date_filed'), 'income_statement_data', ['date_filed'], unique=False)
    op.create_index(op.f('ix_industry_sector_id'), 'industry', ['sector_id'], unique=False)
    op.create_index(op.f('ix_log_log_type'), 'log', ['log_type'], unique=False)
    op.create_unique_constraint(op.f('uq_sector_name'), 'sector', ['name'])
    op.create_unique_constraint(op.f('uq_sector_name_code'), 'sector', ['name_code'])
    op.create_index(op.f('ix_state_info_country_info_id'), 'state_info', ['country_info_id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_state_info_country_info_id'), table_name='state_info')
    op.drop_constraint(op.f('uq_sector_name_code'), 'sector', type_='unique')
    op.drop_constraint(op.f('uq_sector_name'), 'sector', type_='unique')
    op.drop_index(op.f('ix_log_log_type'), table_name='log')
    op.drop_index(op.f('ix_industry_sector_id'), table_name='industry')
    op.drop_index(op.f('ix_income_statement_data_date_filed'), table_name='income_statement_data')
    op.drop_index(op.f('ix_income_statement_data_company_id'), table_name='income_statement_data')
    op.drop_index(op.f('ix_income_statement_data_calendar_date'), table_name='income_statement_data')
    op.drop_index(op.f('ix_exchange_country_info_id'), table_name='exchange')
    op.drop_index(op.f('ix_cron_job_run_log_id'), table_name='cron_job_run')
    op.drop_index(op.f('ix_company_misc_info_company_id'), table_name='company_misc_info')
    op.drop_index(op.f('ix_cash_flow_statement_data_date_filed'), table_name='cash_flow_statement_data')
    op.drop_index(op.f('ix_cash_flow_statement_data_company_id'), table_name='cash_flow_statement_data')
    op.drop_index(op.f('ix_cash_flow_statement_data_calendar_date'), table_name='cash_flow_statement_data')
    op.drop_constraint(op.f('uq_bar_data_company_id'), 'bar_data', type_='unique')
    op.create_unique_constraint('uq_bar_data_company_id', 'bar_data', ['company_id', 'bar_type', 'bar_size', 'bar_date'])
    op.drop_index(op.f('ix_balance_sheet_data_date_filed'), table_name='balance_sheet_data')
    op.drop_index(op.f('ix_balance_sheet_data_company_id'), table_name='balance_sheet_data')
    op.drop_index(op.f('ix_balance_sheet_data_calendar_date'), table_name='balance_sheet_data')
    # ### end Alembic commands ###