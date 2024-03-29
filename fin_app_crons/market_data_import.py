from py_common_utils_gh.os_common_utils import setup_logger, default_log_formatter
from py_common_utils_gh.db_utils.db_utils import SqlAlchemySessionManager
from db.models import *
from db.company_financials import *
from db.db_utils import *
from data_vendors.factory import get_vendor_instance
from data_vendors.vendor import *

import api.routers.company_metric_api

import pandas as pd
import numpy as np
from psycopg2 import *
from sqlalchemy import create_engine, select, insert, exists
from sqlalchemy.orm import sessionmaker

import sys, json, requests, logging, io, math, traceback, datetime, time, math, argparse
import multiprocessing as mp

EXEC_IMPORT_BEGIN = 'exec_import_begin'
EXEC_IMPORT_COMPANIES_LOG_TYPE = 'exc_imp_cpnies'
EXEC_COMPANIES_IMPORT_FUNDAMENTAL_DATA_POINTS_LOG_TYPE = 'exec_imp_fdp'
EXEC_IMPORT_STOCK_PRICES_LOG_TYPE = 'exc_imp_sps'
EXEC_IMPORT_FX_DATA_LOG_TYPE = 'exc_fx_data'

verbose = False

def exec_import_fx_data(session, logger, input_fx_df, bar_size):
    try:
        input_fx_df = input_fx_df.replace({np.nan: None})
        nb_rows = input_fx_df.shape[0]
        current_row = 0
        for idx, row in input_fx_df.iterrows():
            if verbose:
                print("Current row: " + str(current_row) + " out of " + str(nb_rows) + ". Symbol: " + row['symbol'])

            db_fx_data = session.query(CurrencyBarData).filter(CurrencyBarData.symbol == row['symbol'], CurrencyBarData.bar_date == row['date']).first()
            if db_fx_data is None or not db_fx_data.locked:
                fx_data = CurrencyBarData(symbol=row['symbol'], bar_type=data_type_fiat_currency, bar_open=row['open'], bar_high=row['high'], bar_low=row['low'], bar_close=row['close'], \
                                      bar_volume=row['volume'], bar_date=row['date'], bar_size=bar_size)
                    
                if db_fx_data is not None:
                    session.delete(db_fx_data)
                    fx_data.id = db_fx_data.id

                session.add(fx_data)
            
            current_row += 1
    except Exception as gen_ex:
        raise gen_ex

def exec_import_companies(session, logger, input_companies_df, report):
    #log unknown echanges so they can be manually added to db
    unique_exchange_serie = pd.Series(input_companies_df['exchange'].unique())
    unique_exchange_serie = unique_exchange_serie.fillna('Missing')
    for elem in unique_exchange_serie:
        if session.query(exists().where(Exchange.name_code==elem)).scalar() is False:
            msg = "Unknown exchange detected: " + elem
            report.warnings.append(msg)
            logger.warning(msg)
    
    #log unknown sectors so they can be manually added to db
    unique_sector_serie = pd.Series(input_companies_df['sector'].unique())
    unique_sector_serie = unique_sector_serie.fillna('Missing')
    for elem in unique_sector_serie:
        if session.query(exists().where(Sector.name==elem)).scalar() is False:
            msg = "Unknown sector detected: " + elem
            report.warnings.append(msg)
            logger.warning(msg)

    #log unknown industries so they can be manually added to db
    unique_industry_serie = pd.Series(input_companies_df['industry'].unique())
    unique_industry_serie = unique_industry_serie.fillna('Missing')
    for elem in unique_industry_serie:
        if session.query(exists().where(Industry.name==elem)).scalar() is False:
            msg = "Unknown industry detected: " + elem
            report.warnings.append(msg)
            logger.warning(msg)

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
            msg = "None result when fetching first sector matching: " + row['sector']
            report.warnings.append(msg)
            logger.warning(msg)
            continue

        industry_res = session.query(Industry).filter(Industry.name == row['industry']).first()
        if industry_res is None:
            msg = "None result when fetching first industry matching: " + row['industry']
            report.warnings.append(msg)
            logger.warning(msg)
        
        exch_tbl = Exchange.__table__
        stmt = select([exch_tbl.c.id, exch_tbl.c.name]).where(exch_tbl.c.name_code == row['exchange']).limit(1)
        exch_res = session.connection().execute(stmt).first()
        if exch_res is not None:
            if row['isdelisted'] == 'Y':
                row['isdelisted'] = True
            elif row['isdelisted'] == 'N':
                row['isdelisted'] = False
            else:
                msg = "Unknown value in delisted column: " + row['isdelisted']
                report.warnings.append(msg)
                logger.errors(msg)
                continue
            
            
            db_company = session.query(Company).filter(Company.ticker == row['ticker']).first()
            if db_company is not None and db_company.name != row['name']:
                report.tickers_with_name_changes.append((db_company.ticker, db_company.name, row['name']))
                continue 

            db_company_name = session.query(Company).filter(Company.name == row['name']).first()
            if db_company_name is not None and db_company_name.ticker != row['ticker']:
                report.company_names_with_ticker_changes.append((row['name'], db_company_name.ticker, row['ticker']))
                continue 
            

            if db_company is None: #insert
                if session.query(exists().where(Company.name==row['name'])).scalar() is False: #it is possible that there a company is listed with same name with different tickers ...
                    company = Company(ticker=row['ticker'], name=row['name'], delisted=row['isdelisted'])
                    if industry_res is not None:
                        company.industry_id = industry_res.id

                    session.add(company)
                    session.flush()
                    cbop = CompanyBusinessOrProduct(company_id=company.id, code=company.ticker + '_default', display_name='Default business or product')
                    session.add(cbop)
                    cer = CompanyExchangeRelation(company_id=company.id, exchange_id=exch_res.id)
                    session.add(cer)
                    csr = CompanySectorRelation(company_id=company.id, sector_id=sector_res.id)
                    session.add(csr)
                else:
                    logger.warning("Company already exists: " + row['name'])
            elif not db_company.locked: #update
                db_company.name = row['name']
                db_company.delisted = row['isdelisted']
                if industry_res is not None:
                    db_company.industry_id = industry_res.id
                db_cbop = session.query(CompanyBusinessOrProduct).filter(CompanyBusinessOrProduct.company_id == db_company.id).first()
                if db_cbop is None:
                    cbop = CompanyBusinessOrProduct(company_id=db_company.id, code=db_company.ticker + '_default', display_name='Default business or product')
                    session.add(cbop)
        
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
            data_type = DATA_TYPE_QUARTERLY
            if row['dimension'] == 'MRY':
                data_type = DATA_TYPE_ANNUAL
            db_company_quarterly_data = session.query(CompanyFinancialData).filter(CompanyFinancialData.company_id == db_company.id, CompanyFinancialData.calendar_date == row['calendardate'], \
                                                                                   CompanyFinancialData.data_type==data_type).first()
            if db_company_quarterly_data is None or not db_company_quarterly_data.locked:
                company_quarterly_data = CompanyFinancialData(company_id=db_company.id, assets=row['assets'], cashneq=row['cashneq'], investments=row['investments'], investmentsc=row['investmentsc'], investmentsnc=row['investmentsnc'], \
                                                    deferredrev=row['deferredrev'], deposits=row['deposits'], ppnenet=row['ppnenet'], inventory=row['inventory'], taxassets=row['taxassets'], receivables=row['receivables'], \
                                                    payables=row['payables'], intangibles=row['intangibles'], liabilities=row['liabilities'], equity=row['equity'], retearn=row['retearn'], accoci=row['accoci'], assetsc=row['assetsc'], \
                                                    assetsnc=row['assetsnc'], liabilitiesc=row['liabilitiesc'], liabilitiesnc=row['liabilitiesnc'], taxliabilities=row['taxliabilities'], debt=row['debt'], debtc=row['debtc'], \
                                                    debtnc=row['debtnc'], calendar_date=row['calendardate'], date_filed=row['reportperiod'],

                                                    revenue=row['revenue'], cor=row['cor'], opex=row['opex'], sgna=row['sgna'], rnd=row['rnd'], intexp=row['intexp'], taxexp=row['taxexp'], netincdis=row['netincdis'], \
                                                    consolinc=row['consolinc'], netincnci=row['netincnci'], netinc=row['netinc'], prefdivis=row['prefdivis'], netinccmn=row['netinccmn'], \

                                                    capex=row['capex'], ncfbus=row['ncfbus'], ncfi=row['ncfi'], ncfinv=row['ncfinv'], ncff=row['ncff'], ncf=row['ncf'], ncfdebt=row['ncfdebt'], \
                                                    ncfcommon=row['ncfcommon'], ncfdiv=row['ncfdiv'], ncfo=row['ncfo'], ncfx=row['ncfx'], sbcomp=row['sbcomp'], depamor=row['depamor'], \

                                                    shareswa=row['shareswa'], shareswadil=row['shareswadil'], sharesbas=row['sharesbas'],

                                                    fx_usd = row['fxusd'], data_type=data_type
                                                    )
                if db_company_quarterly_data is not None:
                    session.delete(db_company_quarterly_data)
                    company_quarterly_data.id = db_company_quarterly_data.id

                session.add(company_quarterly_data)
            
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
                if idx == nb_rows - 1 or (idx % 10000 == 0 and idx != 0):
                    trans.commit()
                    if idx != nb_rows - 1:
                        trans = conn.begin()
                continue
            db_company = ticker_attributes_map[row['ticker']][0]
            db_exchange = ticker_attributes_map[row['ticker']][1]
            bar_data_tbl = EquityBarData.__table__
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
        try:
            logger.critical(gen_ex, exc_info=True)
            add_cron_job_run_info_to_session(session, current_operation, "Exception", str.encode(traceback.format_exc()), False)
        except Exception as gen_ex:
            logger.critical(gen_ex, exc_info=True)



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
            
            if 'active' not in src or not src['active']:
                continue

            vendor = get_vendor_instance(src['vendor'], config_file_path=src['vendorConfigFilePath'])

            if 'importCompanies' in src and src['importCompanies']:
                current_operation = EXEC_IMPORT_COMPANIES_LOG_TYPE
                #get date the last time companies were imported and use this date as the start date for import
                #res is a (CronJobRun, Log) tuple
                res = session.query(CronJobRun, Log).join(Log).filter(Log.log_type == current_operation).filter(CronJobRun.success == True).order_by(CronJobRun.id.desc()).first()
                

                import_companies_report = ImportCompaniesReport()
                if res is None or 'fullImportCompanies' in src and src['fullImportCompanies']:
                    stamp_without_tz = '' #first time script is ran
                    logger.info("Importing tickers with no date filter.")
                    input_companies_df = vendor.get_all_companies()
                    if input_companies_df is None or input_companies_df.empty:
                        logger.info("No new companies were updated for vendor: " + src['vendor'])
                    else:
                        exec_import_companies(session, logger, input_companies_df, import_companies_report)
                else:
                    if res[0].success is False:
                        logger.warning("Executing companies import when the last import has failed. Last import cron id: " + str(res[0].id))
                    stamp_without_tz = res[1].update_stamp.replace(tzinfo=None)
                    stamp_without_tz = stamp_without_tz.strftime("%Y-%m-%d")
                    logger.info("Importing tickers that were updated after or on: " + stamp_without_tz)
                    input_companies_df = vendor.get_all_companies(from_date=stamp_without_tz)
                    if input_companies_df is None or input_companies_df.empty:
                        logger.info("No new companies were updated for vendor: " + src['vendor'] + " at or after date: " + stamp_without_tz)
                    else:
                        exec_import_companies(session, logger, input_companies_df, import_companies_report)
                
                report_json_str = json.dumps(import_companies_report.__dict__)
                report_json_str_encoded = str.encode(report_json_str)
                add_cron_job_run_info_to_session(session, current_operation, "Successfully imported companies supported by: " + src['vendor'] + " to database.", report_json_str_encoded, True)
            
            if 'importFundamentalDataPoints' in src and src['importFundamentalDataPoints']:
                current_operation = EXEC_COMPANIES_IMPORT_FUNDAMENTAL_DATA_POINTS_LOG_TYPE
                #get date the last time the fundamental data was imported for companies and use this date as the start date for import
                #res is a (CronJobRun, Log) tuple
                res = session.query(CronJobRun, Log).join(Log).filter(Log.log_type == current_operation).filter(CronJobRun.success == True).order_by(CronJobRun.id.desc()).first()
                
                stamp_without_tz = ''
                
                if res is None:
                    logger.info("Importing fundamental data with no date filter.")
                else:
                    if res[0].success is False:
                        logger.warning("Executing companies fundamental data import when the last import has failed. Last import cron id: " + str(res[0].id))
                    stamp_without_tz = res[1].update_stamp.replace(tzinfo=None)
                    stamp_without_tz = stamp_without_tz.strftime("%Y-%m-%d")
                    logger.info("Importing companies fundamental data that was updated after or on: " + stamp_without_tz)
                

                if 'fullImportFundamentals' in src and src['fullImportFundamentals']:
                        stamp_without_tz = ''

                fundamental_data_df = vendor.get_fundamental_data(from_date=stamp_without_tz)
                if fundamental_data_df is None or fundamental_data_df.empty:
                    logger.info("No companies fundamental data was updated for vendor: " + src['vendor'] + " at or after date: " + stamp_without_tz)
                else:
                    exec_import_companies_fundamental_data(session, logger, fundamental_data_df)

                add_cron_job_run_info_to_session(session, current_operation, "Successfully imported companies fundamental data supported by: " + src['vendor'] + " to database.", None, True)

            if 'importStockPrices' in src and src['importStockPrices']:
                if 'importCompanies' in src and src['importCompanies']:
                    session.flush()
                current_operation = EXEC_IMPORT_STOCK_PRICES_LOG_TYPE
                company_attributes = session.query(Company, Exchange, CountryInfo).join(CompanyExchangeRelation, CompanyExchangeRelation.company_id == Company.id).join(Exchange).join(CountryInfo).all()
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
                
                stock_prices_df = vendor.get_historical_bar_data(stamp_without_tz, '', 1, 'd', True, data_type_stock) #might be huge
                
                if stock_prices_df is None or stock_prices_df.empty:
                    logger.info("No stock prices were updated for vendor: " + src['vendor'] + " at or after date: " + stamp_without_tz)
                else:                    
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
                
                if 'fullImportFxData' in src and src['fullImportFxData']:
                        stamp_without_tz = ''
                
                fx_data_df = vendor.get_historical_bar_data(stamp_without_tz, '', 1, 'd', True, data_type_fiat_currency)
                if fx_data_df.empty:
                        logger.info("No fx data was updated for vendor: " + src['vendor'] + " at or after date: " + stamp_without_tz)
                else:
                    exec_import_fx_data(session, logger, fx_data_df, bar_size_day)

                add_cron_job_run_info_to_session(session, current_operation, "Successfully imported fx data supported by: " + src['vendor'] + " to database.", None, True)
                

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
