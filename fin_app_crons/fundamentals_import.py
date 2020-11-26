from py_common_utils_gh.os_common_utils import setup_logger, default_log_formatter
from db_models.models import *
from data_vendors.factory import get_vendor_instance

import pandas as pd
import numpy as np
from sqlalchemy import create_engine, select, insert, exists
from sqlalchemy.orm import sessionmaker

import sys, json, requests, logging, io, math

def exec_import(config_file_path):
    try:
        config_json_content = {}
        
        #For file not found exception. this logger should always be setup with success unless the proper folder/log file have not been created or the permissions for these are inadequate
        logger = setup_logger('root_logger', '/var/log/fin_app/logs.log', True)

        with open(config_file_path, 'r') as f:
            file_content_raw = f.read()
            config_json_content = json.loads(file_content_raw)

            logger = setup_logger('fund_cron_logger', config_json_content['logFilePath'], True)
        
            for src in config_json_content['sources']:
                filtered_out_it = next((x for x in config_json_content['sourcesFilteredOut'] if x == src['vendor'] or x == '*'), None)
                if filtered_out_it != None:
                    filtered_in_it = next((x for x in config_json_content['sourcesFilteredIn'] if x == src['vendor']), None)
                    if filtered_in_it == None:
                        logger.info("The following vendor source is filtered out: " + src['vendor'])
                        continue

                vendor = get_vendor_instance(src['vendor'], config_file_path=src['vendorConfigFilePath'])

                if src['importCompanies']:
                    engine = create_engine(config_json_content['dbConnString'])
                    #override sql alchemy logger specs
                    db_logger = setup_logger('sqlalchemy.engine', config_json_content['logFilePath'], True, default_log_formatter, logging.WARNING)

                    with engine.connect() as connection:
                        input_companies_df = vendor.get_all_companies()

                        Session = sessionmaker(bind=engine)
                        session = Session()  
                        
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
                            sector_res = connection.execute(stmt).first()
                            if sector_res is None:
                                logger.warning("None result when fetching first sector matching: " + row['sector'])
                                continue
                            else:
                                exch_tbl = Exchange.__table__
                                stmt = select([exch_tbl.c.id, exch_tbl.c.name]).where(exch_tbl.c.name_code == row['exchange']).limit(1)
                                exch_res = connection.execute(stmt).first()
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
                                        company = Company(sector_id=sector_res['id'], ticker=row['ticker'], name=row['name'], delisted=row['isdelisted'])
                                        session.add(company)
                                        session.flush() #force company id creation
                                        stmt = t_company_exchange_relation.insert()
                                        session.commit()
                                        connection.execute(stmt, company_id=company.id, exchange_id=exch_res.id) #insert company and exch id in the relation table
                                    elif not db_company.locked: #update
                                        db_company.sector_id = sector_res['id']
                                        db_company.name = row['name']
                                        db_company.delisted = row['isdelisted']
                                        logger.info("The following ticker was updated in the company table: " + db_company.ticker)
                        
                        session.commit()
        
        logger.info("Fundamentals import exited successfully.")
             
    except FileNotFoundError as file_err:
        logger.critical(file_err, exc_info=True)
    except KeyError as key_err:
        logger.critical(key_err, exc_info=True)
    except OSError as os_err:
        logger.critical(os_err, exc_info=True)
    except AttributeError as attr_err:
        logger.critical(attr_err, exc_info=True)
    except TypeError as type_err:
        logger.critical(type_err, exc_info=True)
    except Exception as gen_ex:
        logger.critical(gen_ex, exc_info=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('config_file_path', help="Location of the config file path that will be used.")
    args, unknown = parser.parse_known_args()

    exec_import(args.config_file_path)
