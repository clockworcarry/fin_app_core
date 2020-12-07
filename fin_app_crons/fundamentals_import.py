from py_common_utils_gh.os_common_utils import setup_logger, default_log_formatter
from py_common_utils_gh.db_utils.db_utils import SqlAlchemySessionManager
from db.models import *
from db.db_utils import *
from data_vendors.factory import get_vendor_instance

import pandas as pd
import numpy as np
from sqlalchemy import create_engine, select, insert, exists
from sqlalchemy.orm import sessionmaker

import sys, json, requests, logging, io, math, traceback

EXEC_IMPORT_COMPANIES_LOG_TYPE = 'exc_imp_cpnies'
EXEC_COMPANIES_IMPORT_FUNDAMENTAL_DATA_POINTS_LOG_TYPE = 'exec_imp_fdp'

def exec_import_companies(session, logger, input_companies_df):
    #log unknown echanges so they can be manually added to db
    unique_exchange_serie = pd.Series(input_companies_df['exchange'].unique())
    unique_exchange_serie = unique_exchange_serie.fillna('Missing')
    for elem in unique_exchange_serie:
        if session.query(exists().where(Exchange.name_code==elem)).scalar() is False:
            logger.warning("Unknown exchange detected: " + elem)
    
    #log unknown sectors so they can be manually added to db
    unique_sector_serie = pd.Series(input_companies_df['sector'].unique())
    unique_sector_serie = unique_sector_serie.fillna('Missing')
    for elem in unique_sector_serie:
        if session.query(exists().where(Sector.name==elem)).scalar() is False:
            logger.warning("Unknown sector detected: " + elem)

    #log unknown industries so they can be manually added to db
    unique_industry_serie = pd.Series(input_companies_df['industry'].unique())
    unique_industry_serie = unique_industry_serie.fillna('Missing')
    for elem in unique_industry_serie:
        if session.query(exists().where(Industry.name==elem)).scalar() is False:
            logger.warning("Unknown industry detected: " + elem)

    #save every new company in the db and update the ones that are not locked in the db
    for idx, row in input_companies_df.iterrows():
        row = row.fillna('Missing')
        #get sector_id for company to init new company with it
        tbl = Sector.__table__
        stmt = select([tbl.c.id, tbl.c.name]).where(tbl.c.name == row['sector']).limit(1)
        sector_res = session.connection().execute(stmt).first()
        if sector_res is None:
            logger.warning("None result when fetching first sector matching: " + row['sector'])
            continue
        else:
            exch_tbl = Exchange.__table__
            stmt = select([exch_tbl.c.id, exch_tbl.c.name]).where(exch_tbl.c.name_code == row['exchange']).limit(1)
            exch_res = session.connection().execute(stmt).first()
            if exch_res is not None:
                if row['isdelisted'] == 'Y':
                    row['isdelisted'] = True
                elif row['isdelisted'] == 'N':
                    row['isdelisted'] = False
                else:
                    logger.critical("Unknown value in delisted column: " + row['isdelisted'])
                    continue

                db_company = session.query(Company).filter(Company.ticker == row['ticker']).first()
                if db_company is None: #insert
                    if session.query(exists().where(Company.name==row['name'])).scalar() is False: #it is possible that there a company is listed with same name with different tickers ...
                        company = Company(ticker=row['ticker'], name=row['name'], delisted=row['isdelisted'])
                        session.add(company)
                        session.flush() #force company id creation
                        stmt = t_company_exchange_relation.insert()
                        session.connection().execute(stmt, company_id=company.id, exchange_id=exch_res.id) #insert company and exch id in the relation table
                        stmt = t_company_sector_relation.insert()
                        session.connection().execute(stmt, company_id=company.id, sector_id=sector_res.id) #insert company and sector id in the relation table
                    else:
                        logger.warning("Company already exists: " + row['name'])
                elif not db_company.locked: #update
                    db_company.name = row['name']
                    db_company.delisted = row['isdelisted']
                    logger.info("The following ticker was updated in the company table: " + db_company.ticker)


def exec_import_companies_fundamental_data(session, logger, fundamental_data_df):
    for idx, row in fundamental_data_df.iterrows():
        db_company = session.query(Company).filter(Company.ticker == row['ticker'])
        if db_company is None:
            logger.warning("Company with ticker: " + row['ticker'] + " does not exist in the database.")
            continue
        else:
            db_balance_sheet_data = session.query(BalanceSheetData).filter(BalanceSheetData.company_id==db_company.id, BalanceSheetData.calendar_date==row['calendardate'])
            if db_balance_sheet_data is None:
                logger.info("The balance sheet data was created for the following company: " + db_company.ticker)
            else:
                if not db_balance_sheet_data.locked:
                    logger.info("The balance sheet data was updated for the following company: " + db_company.ticker)
                    balance_sheet_data = BalanceSheetData(company_id=db_company.id, assets=row['assets'], cashneq=row['cashneq'], investments=row['investments'], investmentsc=row['investmentsc'], investmentsnc=row['investmentsnc'], \
                                                          deferredrev=row['deferredrev'], deposits=row['deposits'], ppnenet=row['ppnenet'], inventory=row['inventory'], taxassets=row['taxassets'], receivables=row['receivables'], \
                                                          payables=row['payables'], intangibles=row['intangibles'], liabilities=row['liabilities'], equity=row['equity'], retearn=row['retearn'], accoci=row['accoci'], assetsc=row['assetsc'], \
                                                          assetsnc=row['assetsnc'], liabilitiesc=row['liabilitiesc'], liabilitiesnc=row['liabilitiesnc'], taxliabilities=row['taxliabilities'], debt=row['debt'], debtc=row['debtc'], \
                                                          debtnc=row['debtnc'], equityusd=row['equityusd'], cashnequsd=row['cashnequsd'], debtusd=row['debtusd'], calendar_date=row['calendardate'], period_end_date=row['reportperiod']
                                                         )
                    session.add(balance_sheet_data)

            db_income_statement_data = session.query(IncomeStatementData).filter(IncomeStatementData.company_id==db_company.id, BalanceSheetData.calendar_date==row['calendardate'])
            if not db_income_statement_data.locked:
                income_statement_data = IncomeStatementData(company_id=db_company.id, revenue=row['revenue'], cor=row['cor'], sgna=row['sgna'], rnd=row['rnd'], intexp=row['intexp'], taxexp=row['taxexp'], netincdis=row['netincdis'], \
                                                            consolinc=row['consolinc'], netincnci=row['netincnci'], netinc=row['netinc'], prefdivis=row['prefdivis'], netinccmn=row['netinccmn'], eps=row['eps'], epsdil=row['epsdil'], \
                                                            shareswa=row['shareswa'], shareswadil=row['shareswadil'], ebit=row['ebit'], dps=row['dps'], gp=row['gp'],opinc=row['opinc'], calendar_date=row['calendardate'], \
                                                            period_end_date=row['reportperiod']
                                                           )
                session.add(income_statement_data)

            db_cash_flow_statement_data = session.query(CashFlowStatementData).filter(CashFlowStatementData.company_id==db_company.id, BalanceSheetData.calendar_date==row['calendardate'])
            if not db_cash_flow_statement_data.locked:
                cash_flow_statement_data = CashFlowStatementData(company_id=db_company.id, capex=row['capex'], ncfbus=row['ncfbus'], ncfinv=row['ncfinv'], ncfiny=row['ncfiny'], ncff=row['ncff'], ncfdebt=row['ncfdebt'], \
                                                                 ncfcommon=row['ncfcommon'], ncfdiv=row['ncfdiv'], ncfi=row['ncfi'], ncfo=row['ncfo'], ncfx=row['ncfx'], sbcomp=row['sbcomp'], depamor=row['depamor'], \
                                                                 calendar_date=row['calendardate'], period_end_date=row['reportperiod']
                                                                )
                session.add(cash_flow_statement_data)

            if session.query(exists().where(BalanceSheetData.company_id==db_company.id, BalanceSheetData.calendar_date==row['calendardate'], BalanceSheetData.locked==True)).scalar() is True:
                logger.info("The balance sheet data was updated for the following company: " + db_company.ticker)
            else:
                logger.info("The balance sheet data was created for the following company: " + db_company.ticker)                                                          )
            
            if not db_company.locked:
                db_company.shares_basic = row['sharesbas']


def exec_import(config, session):
    try:
        logger = setup_logger('fund_cron_logger', config['logFilePath'], True)
    
        for src in config['sources']:
            filtered_out_it = next((x for x in config['sourcesFilteredOut'] if x == src['vendor'] or x == '*'), None)
            if filtered_out_it != None:
                filtered_in_it = next((x for x in config['sourcesFilteredIn'] if x == src['vendor']), None)
                if filtered_in_it == None:
                    logger.info("The following vendor source is filtered out: " + src['vendor'])
                    continue

            vendor = get_vendor_instance(src['vendor'], config_file_path=src['vendorConfigFilePath'])
            #override sql alchemy logger specs
            db_logger = setup_logger('sqlalchemy.engine', config['logFilePath'], True, default_log_formatter, logging.WARNING)

            if src['importCompanies']:
                #get date the last time companies were imported and use this date as the start date for import
                #res is a (CronJobRun, Log) tuple
                res = session.query(CronJobRun, Log).join(Log).filter(Log.log_type == EXEC_IMPORT_COMPANIES_LOG_TYPE).order_by(CronJobRun.id.desc()).first()
                if res is None: #first time script is ran
                    logger.info("Importing tickers with no date filter.")
                    input_companies_df = vendor.get_all_companies()
                    if input_companies_df.empty:
                        logger.info("No new companies were updated for vendor: " + src['vendor'])
                    else:
                        exec_import_companies(session, logger, input_companies_df)
                else:
                    if res[0].success is False:
                        logger.warning("Executing companies import when the last import has failed. Last import cron id: " + str(res[0].id))
                    stamp_without_tz = res[1].update_stamp.replace(tzinfo=None)
                    stamp_without_tz = stamp_without_tz.strftime("%Y-%m-%d")
                    logger.info("Importing tickers that were updated after or on: " + stamp_without_tz)
                    input_companies_df = vendor.get_all_companies(from_date=stamp_without_tz)
                    if input_companies_df.empty:
                        logger.info("No new companies were updated for vendor: " + src['vendor'] + " at or after date: " + stamp_without_tz)
                    else:
                        exec_import_companies(session, logger, input_companies_df)
                
                add_cron_job_run_info_to_session(session, EXEC_IMPORT_COMPANIES_LOG_TYPE, "Successfully imported companies supported by: " + src['vendor'] + " to database.", None, True)
            
            if src['importFundamentalDataPoints']:
                #get date the last time the fundamental data was imported for companies and use this date as the start date for import
                #res is a (CronJobRun, Log) tuple
                res = session.query(CronJobRun, Log).join(Log).filter(Log.log_type == EXEC_COMPANIES_IMPORT_FUNDAMENTAL_DATA_POINTS_LOG_TYPE).order_by(CronJobRun.id.desc()).first()
                if res is None: #first time script is ran
                    logger.info("Importing fundamental data with no date filter.")
                    fundamental_data_df = vendor.get_fundamental_data()
                    if fundamental_data_df.empty:
                        logger.info("No new fundamental data was updated for vendor: " + src['vendor'])
                    else:
                        exec_import_companies_fundamental_data(session, logger, fundamental_data_df)
                else:
                    if res[0].success is False:
                        logger.warning("Executing companies fundamental data import when the last import has failed. Last import cron id: " + str(res[0].id))
                    stamp_without_tz = res[1].update_stamp.replace(tzinfo=None)
                    stamp_without_tz = stamp_without_tz.strftime("%Y-%m-%d")
                    logger.info("Importing companies fundamental data that was updated after or on: " + stamp_without_tz)
                    fundamental_data_df = vendor.get_fundamental_data(from_date=stamp_without_tz)
                    if fundamental_data_df.empty:
                        logger.info("No companies fundamental data was updated for vendor: " + src['vendor'] + " at or after date: " + stamp_without_tz)
                    else:
                        exec_import_companies_fundamental_data(session, logger, fundamental_data_df)

                add_cron_job_run_info_to_session(session, EXEC_COMPANIES_IMPORT_FUNDAMENTAL_DATA_POINTS_LOG_TYPE, "Successfully imported companies fundamental data supported by: " + src['vendor'] + " to database.", None, True)

        logger.info("Fundamentals import exited successfully.")
    
    except Exception as gen_ex:
        try:
            logger.critical(gen_ex, exc_info=True)
            add_cron_job_run_info_to_session(session, EXEC_IMPORT_COMPANIES_LOG_TYPE, "Exception", str.encode(traceback.format_exc()), False)
        except Exception as gen_ex:
            logger.critical(gen_ex, exc_info=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Scheduled task to import financial data.')
    parser.add_argument('-c','--config_file_path', help='Absolute config file path', required=True)
    args = vars(parser.parse_args())
    
    try:
        with open(args['config_file_path'], 'r') as f:
            file_content_raw = f.read()
            config_json_content = json.loads(file_content_raw)
            manager = SqlAlchemySessionManager()
            with manager.session_scope(db_url=config_json_content['dbConnString'], template_name='first_session') as session:
                exec_import(config_json_content, session)
    except Exception as gen_ex:
        logger = setup_logger('root_logger', '/var/log/fin_app/logs.log', True)
        logger.critical(gen_ex, exc_info=True)
