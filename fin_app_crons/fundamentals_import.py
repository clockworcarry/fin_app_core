from py_common_utils_gh.os_common_utils import setup_logger
from db_models.models import *
from data_vendors.factory import get_vendor_instance

import pandas as pd
from sqlalchemy import create_engine, select, insert, exists
from sqlalchemy.orm import sessionmaker

import sys, json, requests, logging, io

def exec_import(config_file_path):
    try:
        config_json_content = {}
        
        with open(config_file_path, 'r') as f:
            file_content_raw = f.read()
            config_json_content = json.loads(file_content_raw)

            logging.basicConfig
            logger = setup_logger('fund_cron_logger', config_json_content['logFilePath'])
        
            for src in config_json_content['sources']:
                filtered_out_it = next((x for x in config_json_content['sourcesFilteredOut'] if x == src['vendor']), None)
                if filtered_out_it != None:
                    filtered_in_it = next((x for x in config_json_content['sourcesFilteredIn'] if x == src['vendor']), None)
                    if filtered_in_it == None:
                        continue
                
                vendor = get_vendor_instance(src['vendor'])

                if src['importCompanies']:
                    engine = create_engine(config_json_content['dbConnString'])
                    #override sql alchemy logger specs
                    db_logger  = setup_logger('sqlalchemy.engine', config_json_content['logFilePath'])

                    with engine.connect() as connection:
                        input_companies_df = vendor.get_all_companies()

                        Session = sessionmaker(bind=engine)
                        session = Session()  

                        unknown_exchanges = []
                        unknown_sectors = []

                        known_exchanges = []
                        known_sectors = []
                        
                        #log unknown echanges so they can be manually added to db
                        unique_exchange_serie = input_companies_df['exchange'].unique()
                        for elem in unique_exchange_serie:
                            if session.query(exists().where(Exchange.name_code==elem)).scalar() is False:
                                logger.info("Unknown exchange detected: " + elem)
                                unknown_exchanges.append(elem)
                        
                        #log unknown sectors so they can be manually added to db
                        unique_sector_serie = input_companies_df['sector'].unique()
                        for elem in unique_sector_serie:
                            if session.query(exists().where(Sector.name==elem)).scalar() is False:
                                logger.info("Unknown sector detected: " + elem)
                                unknown_sectors.append(elem)

                        #log unknown industries so they can be manually added to db
                        unique_industry_serie = input_companies_df['industry'].unique()
                        for elem in unique_industry_serie:
                            if session.query(exists().where(Industry.name==elem)).scalar() is False:
                                logger.info("Unknown industry detected: " + elem)
                                unknown_sectors.append(elem)

                        db_existing_tickers_df = pd.read_sql_query('SELECT ticker FROM company', engine) #load all existing company tickers in db to a dataframe
                        #create a new dataframe that will only contain companies that are not already in the db
                        df_diff = input_companies_df.merge(db_existing_tickers_df, how='left', indicator=True).loc[lambda x: x['_merged']=='left_only'] 
                        #save every new company in the db
                        for idx, row in df_diff.iterrows():
                            #get sector_id for company to init new company with it
                            tbl = Sector.__table__
                            stmt = select([tbl.id, tbl.tbl.name]).where(tbl.name == row['sector']).limit(1)
                            sector_res = connection.execute(stmt).first()
                            if sector_res is None:
                                logger.info("None result when fetching first sector matching: " + row['sector'])
                                continue
                            company = Company(sector_id=sector_res['id'], ticker=row['ticker'], name=row['name'], delisted=row['isdelisted'])
                            session.add(company)
                        
                        session.commit()
             
    except FileNotFoundError as file_err:
        logger.critical(str(file_err))
    except KeyError as key_err:
        logger.critical("Key does not exist in dict: " + str(key_err))
    except OSError as os_err:
        logger.critical("Os error caught: " + str(os_err))
    except Exception as gen_ex:
        logger.critical("Generic exception caught: " + str(gen_ex))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('config_file_path', help="Location of the config file path that will be used.")
    args, unknown = parser.parse_known_args()

    exec_import(args.config_file_path)
