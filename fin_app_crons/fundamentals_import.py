from py_common_utils_gh.utils import setup_logger
from db_models.models import *
from data_vendors.sharadar.sharadar import Sharadar
from data_vendors.factory import get_vendor_instance

import pandas as pd
from sqlalchemy import create_engine, select, insert, exists

import sys, json, requests, logging, os_common_utils, io

fundamentals_config_location = os.path.join(sys.path[0], 'fundamentals_import_config.json')

try:
    config_json_content = {}
    
    with open(fundamentals_config_location, 'r') as f:
        file_content_raw = f.read()
        config_json_content = json.loads(file_content_raw)

        logger = setup_logger('fund_cron_logger', config_json_content['logFilePath'])
    
        for src in config_json_content['sources']:
            filtered_out_it = next((x for x in config_json_content['sourcesFilteredOut'] if x == src['vendor']), None)
            if filtered_out_it != None:
                filtered_in_it = next((x for x in config_json_content['sourcesFilteredIn'] if x == src['vendor']), None)
                if filtered_in_it == None:
                    continue
            
            sharadar = get_vendor_instance(src['vendor'])

            if src['importCompanies']:
                engine = create_engine(config_json_content['dbConnString'], echo=True)
                with engine.connect() as connection:
                    input_companies_df = sharadar.get_all_companies()

                    Session = sessionmaker(bind=engine)
                    session = Session()  

                    unknown_exchanges = []
                    unknown_sectors = []

                    known exchanges = []
                    known_sectors = []
                    
                    unique_exchange_serie = input_companies_df['exchange'].unique()
                    for elem in unique_exchange_serie:
                        if Session.query(exists().where(Exchange.name_code==elem)).scalar() is False:
                            logger.info("Unknown exchange detected: " + elem)
                            unknown_exchanges.append(elem)
                    
                    unique_sector_serie = input_companies_df['sector'].unique()
                    for elem in unique_sector_serie:
                        if Session.query(exists().where(Sector.name==elem)).scalar() is False:
                            logger.info("Unknown sector detected: " + elem)
                            unknown_sectors.append(elem)

                    db_existing_tickers_df = pd.read_sql_query('SELECT ticker FROM company', engine) #load all existing company tickers in db to a dataframe
                    #create a new dataframe that will only contain companies that are not already in the db
                    df_diff = input_companies_df.merge(db_existing_tickers_df, how='left', indicator=True).loc[lambda x: x['_merged']!=='left_only'] 
                    #save every new company in the db
                    for idx, row in df_diff.iterrows():
                        #get sector_id for company to init new company with it
                        tbl = Sector.__table__
                        sector_res = connection.execute(select([tbl.id, tbl.tbl.name]))

                        company = Company(sector_id='')
                    


            

            conn = engine.connect([
            supported_exchanges_select = select([t_exchange])
            supported_exchanges_list = conn.execute(supported_exchanges_select)
            df = pd.read_csv(StringIO(r.text))
            for idx, row in df.iterrows():
                if next((x for x in supported_exchanges_list if x["name_code"] == row["exchange"]), None) == None:
                    pass

             
except FileNotFoundError as file_err:
    logging.critical(str(file_err))
except KeyError as key_err:
    logging.critical("Key does not exist in dict: " + str(key_err))
except OSError as os_err:
    logging.critical("Os error caught: " + str(os_err))
except Exception as gen_ex:
    logging.critical("Generic exception caught: " + str(gen_ex))


