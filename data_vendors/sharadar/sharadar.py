from data_vendors.vendor import Vendor
from py_common_utils_gh.os_common_utils import setup_logger

import pandas as pd

import requests, io, os, sys, json

class Sharadar(Vendor):
    config = {}

    def __init__(self, **kwargs):
        if kwargs['config_file_path'] is None:
            raise TypeError("Missing mandatory log_file_path argument.")

        with open(kwargs['config_file_path'], 'r') as f:
            config_raw = f.read()
            self.config = json.loads(config_raw)
    
    def get_all_companies(self, **kwargs):
        full_url = self.config['domainUrl'] + "/" + self.config['apiVersion'] + "/" + self.config['baseUrlExtension'] + "/" + self.config['tickerTableUrlExtension'] + \
                   "&" + "api_key=" + self.config['apiKey'] + "&qopts.export=true"

        if 'from_date' in kwargs:
            full_url = full_url + "&lastupdated.gte=" + kwargs['from_date']
        
        r = requests.get(full_url)
        
        if r.status_code == 200:
            r = r.json()
            zip_url = r['datatable_bulk_download']['file']['link']
            zip_req = requests.get(zip_url, stream=True)
            if zip_req.status_code == 200:
                df = pd.read_csv(io.BytesIO(zip_req.content), compression='zip')
                if df.empty:
                    return df
                else:
                    return df[['ticker', 'name', 'exchange', 'isdelisted', 'famaindustry', 'sector', 'industry', 'location']]
            else:
                raise Exception("Sharadar returned http " + str(r.status_code) + " for method get_all_companies while trying to get zip data.")
        else:
            raise Exception("Sharadar returned http " + str(r.status_code) + " for method get_all_companies while trying to get zip link.")

    def get_all_companies_fundamental_datapoints(self, **kwargs):
        full_url = self.config['domainUrl'] + "/" + self.config['apiVersion'] + "/" + self.config['baseUrlExtension'] + "/" + self.config['fundamentalDataPointsTableUrlExtension'] + \
                   "&" + "api_key=" + self.config['apiKey'] + "&qopts.export=true"
        r = requests.get(full_url)
        
        if r.status_code == 200:
            r = r.json()
            zip_url = r['datatable_bulk_download']['file']['link']
            zip_req = requests.get(zip_url, stream=True)
            if zip_req.status_code == 200:
                df = pd.read_csv(io.BytesIO(zip_req.content), compression='zip')
                return df
            else:
                raise Exception("Sharadar returned http " + str(r.status_code) + " for method get_all_companies_fundamental_datapoints while trying to get zip data.")
        else:
            raise Exception("Sharadar returned http " + str(r.status_code) + " for method get_all_companies_fundamental_datapoints while trying to get zip link.")

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