from py_common_utils_gh.os_common_utils import setup_logger, default_log_formatter
from py_common_utils_gh.db_utils.db_utils import SqlAlchemySessionManager
from db.models import *
from db.db_utils import *
from data_vendors.factory import get_vendor_instance
from data_vendors.vendor import *

import pandas as pd
import numpy as np
from psycopg2 import *
from sqlalchemy import create_engine, select, insert, exists
from sqlalchemy.orm import sessionmaker

import sys, json, requests, logging, io, math, traceback, datetime, time, math
import multiprocessing as mp

EXEC_IMPORT_BEGIN = 'exec_import_begin'
EXEC_IMPORT_COMPANIES_LOG_TYPE = 'exc_imp_cpnies'
EXEC_COMPANIES_IMPORT_FUNDAMENTAL_DATA_POINTS_LOG_TYPE = 'exec_imp_fdp'
EXEC_IMPORT_STOCK_PRICES_LOG_TYPE = 'exc_imp_sps'
EXEC_IMPORT_FX_DATA_LOG_TYPE = 'exc_fx_data'

verbose = False

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

    nb_rows = input_companies_df.shape[0]
    current_row = 0
    #save every new company in the db and update the ones that are not locked in the db
    for idx, row in input_companies_df.iterrows():
        if verbose:
            print("Current row: " + str(current_row) + " out of " + str(nb_rows) + ". Ticker: " + row['ticker'])
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
                
                db_company = session.query(Company).filter(Company.name == row['name']).first()
                if db_company is not None and not db_company.locked and db_company.ticker != row['ticker']: # company ticker was changed but name stayed the same
                    logger.info("Company with name " + row['name'] + " ticker changed from " + db_company.ticker + " to " + row['ticker'])
                    db_company.ticker = row['ticker']

                db_company = session.query(Company).filter(Company.ticker == row['ticker']).first()
                if db_company is not None and not db_company.locked and db_company.name != row['name']: # company name was changed but ticker stayed the same
                    logger.info("Company with ticker " + row['ticker'] + " name changed from " + db_company.name + " to " + row['name'])
                    db_company.name = row['name']

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
        
        current_row += 1

def exec_import_companies_fundamental_data(session, logger, fundamental_data_df):
    fundamental_data_df = fundamental_data_df.replace({np.nan: None})
    nb_rows = fundamental_data_df.shape[0]
    current_row = 0
    for idx, row in fundamental_data_df.iterrows():
        if verbose:
            print("Current row: " + str(current_row) + " out of " + str(nb_rows) + ". Ticker: " + row['ticker'])
        db_company = session.query(Company).filter(Company.ticker == row['ticker']).first()
        if db_company is None:
            logger.warning("Company with ticker: " + row['ticker'] + " does not exist in the database.")
            continue
        else:
            db_balance_sheet_data = session.query(BalanceSheetData).filter(BalanceSheetData.company_id == db_company.id, BalanceSheetData.calendar_date == row['calendardate']).first()
            if db_balance_sheet_data is None or not db_balance_sheet_data.locked:
                balance_sheet_data = BalanceSheetData(company_id=db_company.id, assets=row['assets'], cashneq=row['cashneq'], investments=row['investments'], investmentsc=row['investmentsc'], investmentsnc=row['investmentsnc'], \
                                                    deferredrev=row['deferredrev'], deposits=row['deposits'], ppnenet=row['ppnenet'], inventory=row['inventory'], taxassets=row['taxassets'], receivables=row['receivables'], \
                                                    payables=row['payables'], intangibles=row['intangibles'], liabilities=row['liabilities'], equity=row['equity'], retearn=row['retearn'], accoci=row['accoci'], assetsc=row['assetsc'], \
                                                    assetsnc=row['assetsnc'], liabilitiesc=row['liabilitiesc'], liabilitiesnc=row['liabilitiesnc'], taxliabilities=row['taxliabilities'], debt=row['debt'], debtc=row['debtc'], \
                                                    debtnc=row['debtnc'], equityusd=row['equityusd'], cashnequsd=row['cashnequsd'], debtusd=row['debtusd'], calendar_date=row['calendardate'], date_filed=row['reportperiod']
                                                    )
                if db_balance_sheet_data is not None:
                    session.delete(db_balance_sheet_data)
                    balance_sheet_data.id = db_balance_sheet_data.id

                session.add(balance_sheet_data)

            db_income_statement_data = session.query(IncomeStatementData).filter(IncomeStatementData.company_id == db_company.id, IncomeStatementData.calendar_date == row['calendardate']).first()           
            if db_income_statement_data is None or not db_income_statement_data.locked:
                income_statement_data = IncomeStatementData(company_id=db_company.id, revenue=row['revenue'], cor=row['cor'], sgna=row['sgna'], rnd=row['rnd'], intexp=row['intexp'], taxexp=row['taxexp'], netincdis=row['netincdis'], \
                                                        consolinc=row['consolinc'], netincnci=row['netincnci'], netinc=row['netinc'], prefdivis=row['prefdivis'], netinccmn=row['netinccmn'], eps=row['eps'], epsdil=row['epsdil'], \
                                                        shareswa=row['shareswa'], shareswadil=row['shareswadil'], ebit=row['ebit'], dps=row['dps'], gp=row['gp'],opinc=row['opinc'], calendar_date=row['calendardate'], \
                                                        date_filed=row['reportperiod']
                                                        )
            
                if db_income_statement_data is not None:
                    session.delete(db_income_statement_data)
                    income_statement_data.id = db_income_statement_data.id

                session.add(income_statement_data)

            db_cash_flow_statement_data = session.query(CashFlowStatementData).filter(CashFlowStatementData.company_id == db_company.id, CashFlowStatementData.calendar_date == row['calendardate']).first()
            if db_cash_flow_statement_data is None or not db_cash_flow_statement_data.locked:
                cash_flow_statement_data = CashFlowStatementData(company_id=db_company.id, capex=row['capex'], ncfbus=row['ncfbus'], ncfi=row['ncfi'], ncfinv=row['ncfinv'], ncff=row['ncff'], ncfdebt=row['ncfdebt'], \
                                                                ncfcommon=row['ncfcommon'], ncfdiv=row['ncfdiv'], ncfo=row['ncfo'], ncfx=row['ncfx'], sbcomp=row['sbcomp'], depamor=row['depamor'], \
                                                                calendar_date=row['calendardate'], date_filed=row['reportperiod']
                                                            )
                if db_cash_flow_statement_data is not None:
                    session.delete(db_cash_flow_statement_data)
                    cash_flow_statement_data.id = db_cash_flow_statement_data.id

                session.add(cash_flow_statement_data)

            db_company_misc_info = session.query(CompanyMiscInfo).filter(CompanyMiscInfo.company_id == db_company.id, CompanyMiscInfo.date_recorded == row['calendardate']).first()
            if db_company_misc_info is None:
                company_misc_info = CompanyMiscInfo(company_id=db_company.id, shares_bas=row['sharesbas'], date_recorded=row['calendardate'])
                session.add(company_misc_info)
            elif not db_company_misc_info.locked:
                db_company_misc_info.shares_bas = row['sharesbas']
            
        current_row += 1


def exec_import_stock_prices(db_conn_str, session_name, logger, stock_prices_df, ticker_attributes_map, bar_size):
    manager = SqlAlchemySessionManager()
    try:
        stock_prices_df = stock_prices_df.replace({np.nan: None})
        engine = create_engine(db_conn_str, echo=False)
        nb_rows = stock_prices_df.shape[0]
        conn = engine.connect()
        trans = None
        trans = conn.begin()
        current_row = 0
        for idx, row in stock_prices_df.iterrows():
            if verbose and (idx % 1000 == 0):
                print("Current row: " + str(current_row) + " out of " + str(nb_rows) + ". Ticker: " + row['ticker'])
            if row['ticker'] not in ticker_attributes_map:
                #logger.warning("Company with ticker " + row['ticker'] + " was not loaded from the db. Stock prices will not be saved.")
                continue
            db_company = ticker_attributes_map[row['ticker']][0]
            db_exchange = ticker_attributes_map[row['ticker']][1]
            bar_data_tbl = BarData.__table__
            stmt = select([bar_data_tbl.c.id, bar_data_tbl.c.locked]).where((bar_data_tbl.c.company_id == db_company.id) & (bar_data_tbl.c.bar_date == row['date'])).limit(1)                  
            db_bar_data = conn.execute(stmt).fetchone()
            #db_bar_data = session.query(BarData).filter(BarData.company_id == db_company.id, BarData.bar_date == row['date']).first()
            if db_bar_data is None or not db_bar_data.locked:
                '''bar_data = BarData(company_id=db_company.id, exchange_id=db_exchange.id, bar_type=BAR_TYPE_STOCK_TRADE, bar_open=row['open'], bar_high=row['high'], bar_low=row['low'], bar_close=row['close'], \
                                    bar_volume=row['volume'], bar_date=row['date'], bar_size=bar_size)'''
                if db_bar_data is None:
                    stmt = bar_data_tbl.insert()
                    conn.execute(stmt, company_id=db_company.id, exchange_id=db_exchange.id, bar_type=BAR_TYPE_STOCK_TRADE, bar_open=row['open'], bar_high=row['high'], 
                                                        bar_low=row['low'], bar_close=row['close'], \
                                                        bar_volume=row['volume'], bar_date=row['date'], bar_size=bar_size)
                else:
                    stmt = bar_data_tbl.update().values(id=db_bar_data.id, company_id=db_company.id, exchange_id=db_exchange.id, bar_type=BAR_TYPE_STOCK_TRADE, bar_open=row['open'], bar_high=row['high'], 
                                                        bar_low=row['low'], bar_close=row['close'], \
                                                        bar_volume=row['volume'], bar_date=row['date'], bar_size=bar_size).where(bar_data_tbl.c.id == db_bar_data.id)
                    conn.execute(stmt)
                
                if idx == nb_rows - 1 or (idx % 10000 == 0 and idx != 0):
                    trans.commit()
                    if idx != nb_rows - 1:
                        trans = conn.begin()
            
            current_row += 1
    except Exception as gen_ex:
        if trans is not None:
            trans.rollback()
        raise gen_ex



def exec_import(config, session):
    current_operation = EXEC_IMPORT_BEGIN
    try:
        logger = setup_logger('fund_cron_logger', config['logFilePath'], True)
        #override sql alchemy logger specs
        db_logger = setup_logger('sqlalchemy.engine', config['logFilePath'], True, default_log_formatter, logging.WARNING)

        for src in config['sources']:
            filtered_out_it = next((x for x in config['sourcesFilteredOut'] if x == src['vendor'] or x == '*'), None)
            if filtered_out_it != None:
                filtered_in_it = next((x for x in config['sourcesFilteredIn'] if x == src['vendor']), None)
                if filtered_in_it == None:
                    logger.info("The following vendor source is filtered out: " + src['vendor'])
                    continue
            
            vendor = get_vendor_instance(src['vendor'], config_file_path=src['vendorConfigFilePath'])

            if 'importCompanies' in src and src['importCompanies']:
                current_operation = EXEC_IMPORT_COMPANIES_LOG_TYPE
                #get date the last time companies were imported and use this date as the start date for import
                #res is a (CronJobRun, Log) tuple
                res = session.query(CronJobRun, Log).join(Log).filter(Log.log_type == current_operation).filter(CronJobRun.success == True).order_by(CronJobRun.id.desc()).first()
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
                
                add_cron_job_run_info_to_session(session, current_operation, "Successfully imported companies supported by: " + src['vendor'] + " to database.", None, True)
            
            if 'importFundamentalDataPoints' in src and src['importFundamentalDataPoints']:
                current_operation = EXEC_COMPANIES_IMPORT_FUNDAMENTAL_DATA_POINTS_LOG_TYPE
                #get date the last time the fundamental data was imported for companies and use this date as the start date for import
                #res is a (CronJobRun, Log) tuple
                res = session.query(CronJobRun, Log).join(Log).filter(Log.log_type == current_operation).filter(CronJobRun.success == True).order_by(CronJobRun.id.desc()).first()
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

                add_cron_job_run_info_to_session(session, current_operation, "Successfully imported companies fundamental data supported by: " + src['vendor'] + " to database.", None, True)

            if 'importStockPrices' in src and src['importStockPrices']:
                current_operation = EXEC_IMPORT_STOCK_PRICES_LOG_TYPE
                company_attributes = session.query(Company, Exchange, CountryInfo).join(t_company_exchange_relation, t_company_exchange_relation.c.company_id == Company.id).join(Exchange).join(CountryInfo).all()
                ticker_attributes_map = {}
                for attr in company_attributes:
                    ticker_attributes_map[attr[0].ticker] = attr
                #get date the last time stock prices were imported and use this date as the start date for import
                #res is a (CronJobRun, Log) tuple
                res = session.query(CronJobRun, Log).join(Log).filter(Log.log_type == current_operation).filter(CronJobRun.success == True).order_by(CronJobRun.id.desc()).first()
                stamp_without_tz = ''
                if res is None: #first time script is ran
                    logger.info("Importing stock prices with no date filter.")
                else:
                    if res[0].success is False:
                        logger.warning("Executing stock prices import when the last import has failed. Last import cron id: " + str(res[0].id))
                    stamp_without_tz = res[1].update_stamp.replace(tzinfo=None)
                    stamp_without_tz = stamp_without_tz.strftime("%Y-%m-%d")
                    logger.info("Importing stock prices that was updated after or on: " + stamp_without_tz)

                if 'fullImportStockPrices' in src and src['fullImportStockPrices']:
                        stamp_without_tz = ''
                
                stock_prices_df = vendor.get_historical_bar_data_full(stamp_without_tz, '', 1, 'd', True) #might be huge
                    
                if 'tickersFilteredOut' in src:
                    for ticker in src['tickersFilteredOut']:
                        logger.info("The following ticker is filtered out for stock prices import: " + ticker)
                        stock_prices_df = stock_prices_df[stock_prices_df['ticker'] != ticker]
                    
                if 'exchangesFilteredOut' in src:
                    for exch in src['exchangesFilteredOut']:
                        logger.info("The following exchange is filtered out for stock prices import: " + exch)
                        stock_prices_df = stock_prices_df[stock_prices_df['exchange'] != exch]

                list_df = []
                nb_rows_df = stock_prices_df.shape[0]          
                i = 0
                nb_rows_per_df = 2000000
                
                while i <= nb_rows_df:
                    if (nb_rows_df - i) < nb_rows_per_df:
                        list_df.append(stock_prices_df.iloc[i:i + (nb_rows_df - i + 1)])
                    else:
                        list_df.append(stock_prices_df.iloc[i:i + nb_rows_per_df])
                    i += nb_rows_per_df

                print("Dataframe views created. There are " + str(len(list_df)) + " dataframes.")

                processes = []
                for idx, df in enumerate(list_df):
                    proc = mp.Process(target=exec_import_stock_prices, args=(config['dbConnString'], 'stk_imp_proc_' + str(idx), logger, df, ticker_attributes_map, str(1) + ' ' + src['importStockPricesResolution']))
                    processes.append(proc)

                for idx, proc in enumerate(processes):
                    print("Starting process " + str(idx + 1) + " out of " + str(len(processes)))
                    proc.start()

                for idx, proc in enumerate(processes):
                    proc.join()
                    print("Process " + str(idx + 1) + " ended")

                print("Stock prices import done.")
                #processes = [Process(target=exec_import_stock_prices, args=(session, logger, stock)) for x in range(len(list_df))]
                #exec_import_stock_prices(session, logger, stock_prices_df, ticker_attributes_map, str(1) + ' ' + src['importStockPricesResolution'])
                add_cron_job_run_info_to_session(session, current_operation, "Successfully imported stock prices supported by: " + src['vendor'] + " to database.", None, True)

            if 'importFxData' in src and src['importFxData']:
                current_operation = EXEC_IMPORT_FX_DATA_LOG_TYPE
                res = session.query(CronJobRun, Log).join(Log).filter(Log.log_type == current_operation).filter(CronJobRun.success == True).order_by(CronJobRun.id.desc()).first()
                stamp_without_tz = ''
                if res is None: #first time script is ran
                    logger.info("Importing fx data with no date filter.")
                else:
                    if res[0].success is False:
                        logger.warning("Executing fx data import when the last import has failed. Last import cron id: " + str(res[0].id))
                    stamp_without_tz = res[1].update_stamp.replace(tzinfo=None)
                    stamp_without_tz = stamp_without_tz.strftime("%Y-%m-%d")
                    logger.info("Importing fx data that was updated after or on: " + stamp_without_tz)
                
                fx_data_df = vendor.get_historical_bar_data(stamp_without_tz, '', 1, 'd', True) #might be huge
                

        logger.info("Market data import exited successfully.")
    
    except Exception as gen_ex:
        try:
            logger.critical(gen_ex, exc_info=True)
            add_cron_job_run_info_to_session(session, current_operation, "Exception", str.encode(traceback.format_exc()), False)
        except Exception as gen_ex:
            logger.critical(gen_ex, exc_info=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Scheduled task to import financial data.')
    parser.add_argument('-c','--config_file_path', help='Absolute config file path', required=True)
    parser.add_argument('-v','--verbose', help='Verbose', default=True)
    args = vars(parser.parse_args())
    
    verbose = args['verbose']

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
