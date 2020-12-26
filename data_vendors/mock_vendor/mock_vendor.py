from data_vendors.vendor import Vendor
from py_common_utils_gh.os_common_utils import setup_logger

import pandas as pd

from datetime import datetime
import requests, io, os, sys, json

class MockVendor(Vendor):

    def __init__(self, **kwargs):
        if 'config_file_path' not in kwargs:
            raise TypeError("Missing mandatory log_file_path argument.")

        with open(kwargs['config_file_path'], 'r') as f:
            config_raw = f.read()
            if len(config_raw) > 0:
                self.config = json.loads(config_raw)

    def get_all_companies(self, **kwargs):
        if 'from_date' in kwargs:
            df = pd.read_csv(kwargs['from_date'] + '_' + self.config['company_file_path'])
        else:
            df = pd.read_csv(self.config['company_file_path'])
        return df[['ticker', 'name', 'exchange', 'isdelisted', 'famaindustry', 'sector', 'industry', 'location']]

    def get_fundamental_data(self, **kwargs):
        df = pd.read_csv(self.config['company_file_path'])
        return df

    def get_historical_bar_data(self, retrieval_specs, start_date, end_date, bar_size, bar_size_unit, only_regular_hours):
        if start_date == '':
            df = pd.DataFrame({'date': ['2200-01-01', '2200-02-02', '2201-01-01'], 'open': [100, 200, 300], 'high': [105, 210, 301], 'low': [98, 150, 290], 'close': [99, 155, 300.25], \
                               'volume': [200, 300, 400]})
            return df
        else:
            df = pd.DataFrame({'date': ['2200-01-01', '2200-02-02', '2201-01-01', '2202-10-10', '1980-01-01'], 'open': [1000, 2000, 3000, 4000, 5000], 'high': [1050, 2100, 3010, 5000, 6000], 'low': [980, 1500, 2900, 6000, 7000], 'close': [990, 1550, 3000.250, 7000, 8000], \
                               'volume': [2000, 3000, 4000, 5000, 6000]})
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            df['date'] = pd.to_datetime(df['date'])
            return df[df['date'] >= start_date]

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