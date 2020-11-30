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

            if src['importCompanies']:
                #override sql alchemy logger specs
                db_logger = setup_logger('sqlalchemy.engine', config['logFilePath'], True, default_log_formatter, logging.WARNING)
                
                input_companies_df = vendor.get_all_companies()
                
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
                                #only update if the data has changed
                                if db_company.name != row['name'] or db_company.delisted != row['isdelisted']:
                                    db_company.name = row['name']
                                    db_company.delisted = row['isdelisted']
                                    logger.info("The following ticker was updated in the company table: " + db_company.ticker)
        
        add_cron_job_run_info_to_session(session, 'exc_imp_fund', "Fundamentals import exited successfully.", None, True)

        logger.info("Fundamentals import exited successfully.")
    
    except Exception as gen_ex:
        try:
            logger.critical(gen_ex, exc_info=True)
            add_cron_job_run_info_to_session(session, 'exc_imp_fund', "Exception", str.encode(traceback.format_exc()), False)
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
