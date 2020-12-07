from data_vendors.vendor import Vendor
from py_common_utils_gh.os_common_utils import setup_logger

import pandas as pd

import requests, io, os, sys, json

class MockVendor(Vendor):

    def __init__(self, **kwargs):
        if kwargs['config_file_path'] is None:
            raise TypeError("Missing mandatory log_file_path argument.")

        with open(kwargs['config_file_path'], 'r') as f:
            config_raw = f.read()
            self.config = json.loads(config_raw)

    def get_all_companies(self, **kwargs):
        if 'from_date' in kwargs:
            df = pd.read_csv(kwargs['from_date'] + '_' + self.config['company_file_path'])
        else:
            df = pd.read_csv(self.config['company_file_path'])
        return df[['ticker', 'name', 'exchange', 'isdelisted', 'famaindustry', 'sector', 'industry', 'location']]

    def get_fundamental_data(self, **kwargs):
        pass

if __name__ == "__main__":
    try:
        mock_vendor = MockVendor()
        logger = setup_logger('mock_vendor_logger', '/home/ghelie/fin_app/dev_logs/logs.log')
        df = mock_vendor.get_all_companies()
        print(df)
    except KeyError as key_err:
        print(str(key_err))
        logger.info(str(key_err))
    except ValueError as val_err:
        print(str(val_err))
        logger.info(str(val_err))
    except Exception as gen_ex:
        print(str(gen_ex))
        logger.info(str(gen_ex))