from data_vendors.vendor import Vendor
from py_common_utils_gh.os_common_utils import setup_logger

import pandas as pd

import requests, io, os, sys, json

class MockVendor(Vendor):

    def get_all_companies(self, **kwargs):
        #absolute_path = os.path.join(sys.path[0], 'companies.csv')
        df = pd.read_csv('/media/ext_hdd/experiments/database/companies.csv')
        return df[['ticker', 'name', 'exchange', 'isdelisted', 'famaindustry', 'sector', 'industry', 'location']]

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