from data_vendors.vendor import Vendor
from py_common_utils_gh.os_common_utils import setup_logger

import pandas as pd

import requests, io, os, sys, json

class Sharadar(Vendor):
    config = {}

    def __init__(self, config_location):      
        absolute_path = os.path.join(sys.path[0], config_location)
        with open(absolute_path, 'r') as f:
            config_raw = f.read()
            Sharadar.config = json.loads(config_raw)
    
    def get_all_companies(self, **kwargs):
        full_url = Sharadar.config['domainUrl'] + "/" + Sharadar.config['apiVersion'] + "/" + Sharadar.config['baseUrlExtension'] + "/" + Sharadar.config['tickerTableUrlExtension'] + "&" + "api_key=" + Sharadar.config['apiKey'] + "&qopts.export=true"
        
        r = requests.get(full_url)
        
        if r.status_code == 200:
            r = r.json()
            zip_url = r['datatable_bulk_download']['file']['link']
            zip_req = requests.get(zip_url, stream=True)
            if zip_req.status_code == 200:
                df = pd.read_csv(io.BytesIO(zip_req.content), compression='zip')
                return df[['ticker', 'name', 'exchange', 'isdelisted', 'famaindustry', 'sector', 'industry', 'location']]
            else:
                raise Exception("Sharadar returned http " + str(r.status_code) + " for method get_all_companies while trying to get zip data.")
        else:
            raise Exception("Sharadar returned http " + str(r.status_code) + " for method get_all_companies while trying to get zip link.")

if __name__ == "__main__":
    try:
        sharadar = Sharadar('sharadar_config.json')
        logger = setup_logger('sharadar_logger', '/home/ghelie/fin_app/dev_logs/logs.log')
        df = sharadar.get_all_companies()
        df.to_csv('test.csv')
    except KeyError as key_err:
        print(str(key_err))
        logger.info(str(key_err))
    except ValueError as val_err:
        print(str(val_err))
        logger.info(str(val_err))
    except Exception as gen_ex:
        print(str(gen_ex))
        logger.info(str(gen_ex))