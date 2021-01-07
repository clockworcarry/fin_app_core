from db.models import *
from py_common_utils_gh.db_utils.db_utils import SqlAlchemySessionManager

from sqlalchemy import *
from sqlalchemy.orm import sessionmaker

import logging, os, sys, json, datetime

import pandas as pd

try:
    manager = SqlAlchemySessionManager()
    with manager.session_scope(db_url='postgresql://postgres:navo1234@localhost:5432/Fin_App_Core_Db_Dev', template_name='first_session') as session:
        '''bal_sheet_data = session.query(BalanceSheetData).join(Company).filter((Company.ticker == 'AAPL') | (Company.ticker == 'MSFT') | (Company.ticker == 'ZM')).all()
        inc_stmt_data = session.query(IncomeStatementData).join(Company).filter((Company.ticker == 'AAPL') | (Company.ticker == 'MSFT') | (Company.ticker == 'ZM')).all()
        cf_stmt_data = session.query(CashFlowStatementData).join(Company).filter((Company.ticker == 'AAPL') | (Company.ticker == 'MSFT') | (Company.ticker == 'ZM')).all()'''
        df = pd.read_sql("SELECT revenue, netinc, shareswa FROM income_statement_data JOIN company on company.id = income_statement_data.company_id \
                          AND company.ticker = 'ZM' or company.ticker = 'AAPL' or company.ticker = 'MSFT';", session.bind)
        display(df)
except Exception as gen_ex:
    print(gen_ex)