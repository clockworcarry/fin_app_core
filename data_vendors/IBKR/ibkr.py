from data_vendors.vendor import *
from ib_insync import *
from py_common_utils_gh.os_common_utils import setup_logger, default_log_formatter

import pandas as pd

from datetime import datetime
import logging, json, math, time

class IBKR(Vendor):
    current_client_id = 1
    @staticmethod
    def handle_error(req_id, err_code, err_str, contract):
        logger = logging.getLogger('ib_insync.ib')
        if err_code == 2106:
            logger.info("Ib event fired. Req id: " + str(req_id) + ", event code: " + str(err_code) + ", event str: " + err_str + ".")
        else:
            logger.error("Ib error caught. Req id: " + str(req_id) + ", err code: " + str(err_code) + ", err str: " + err_str + ".")

    def __init__(self, **kwargs):
        if not 'config_file_path' in kwargs:
            raise TypeError("Missing mandatory log_file_path argument.")
        if IBKR.current_client_id == 32:
            raise RuntimeError("Maximum simultaneous connections reached for vendor IBKR.")

        with open(kwargs['config_file_path'], 'r') as f:
            config_raw = f.read()
            self.config = json.loads(config_raw)
        
        if 'clientId' in self.config:
            IBKR.current_client_id = self.config['clientId']
        
        self.ib = IB()
        self.ib.connect(self.config['host'], self.config['port'], clientId=IBKR.current_client_id, readonly=self.config['readOnly'])
        self.ib_insync_logger = setup_logger('ib_insync.ib', self.config['logFilePath'], True)
        self.logger = setup_logger('ibkr_logger', self.config['logFilePath'], True)
        self.ib.errorEvent += IBKR.handle_error
        IBKR.current_client_id += 1

    def get_fundamental_data(self, **kwargs):
        raise NotImplementedError("get_fundamental_data not implemented for ibkr vendor.")

    def get_all_companies(self, **kwargs):
        raise NotImplementedError("get_all_companies not implemented for ibkr vendor.")

    def decompose_time(start_date_obj, end_date_obj):
        years_diff = end_date_obj.year - start_date_obj.year
        days_diff = end_date_obj.day - start_date_obj.day
        hours_diff = end_date_obj.hour - start_date_obj.hour
        minutes_diff = end_date_obj.minute - start_date_obj.minute
        seconds_diff = end_date_obj.second - start_date_obj.second
    
    def get_historical_bar_data(self, start_date, end_date, bar_size, bar_size_unit, only_regular_hours, data_type):
        if start_date == '':
            start_date_obj = datetime(1900, 1, 1) #set to a very low date so we get entire history
        else:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
        if end_date == '':
            end_date_obj = datetime.now()
        else:            
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
        self.validate_get_historical_bar_data(start_date_obj, end_date_obj, bar_size, bar_size_unit)
        
        what_to_show = ''
        contracts = []

        if data_type == data_type_stock:
            what_to_show = 'TRADES'
            self.logger.warning("Tried to import stock prices using vendor IBKR - not supported.")
            return pd.DataFrame()
        elif data_type == data_type_fiat_currency:
            if 'currencyPairs' in self.config:
                fx_pairs = self.config['currencyPairs']
                what_to_show = 'MIDPOINT'
                for fp in fx_pairs:
                    contract = Contract()
                    fp_toks = fp.split('.')
                    if len(fp_toks) != 2:
                        self.logger.warning("fp " + fp + "ignored because its format is not valid.")
                        continue
                    contract.symbol = fp_toks[0]
                    contract.currency = fp_toks[1]
                    contract.secType = 'CASH'
                    contract.exchange = 'IDEALPRO'
                    self.ib.qualifyContracts(contract)
                    if contract.conId == 0:
                        self.logger.warning("Failed to qualify contract with symbol: " + contract.symbol + " for vendor IBKR.")
                        continue
                    contracts.append(contract)
            else:
                self.logger.warning("No currency pairs array in IBKR config. No fx data will be imported.")
                return pd.DataFrame()
        
        df_res = None
        if bar_size_unit == 'd' or bar_size_unit == 'days':
            bar_size_unit = 'day'
        bar_size_setting = str(bar_size) + ' ' + bar_size_unit
        for c in contracts:
            years_diff = end_date_obj.year - start_date_obj.year
            months_diff = end_date_obj.month - start_date_obj.month
            days_diff = end_date_obj.day - start_date_obj.day
            hours_diff = end_date_obj.hour - start_date_obj.hour
            #end_date_time = end_date_obj
            end_date_time = datetime(2006, 1, 1)
            bars_list = []
            while years_diff > 0:
                if years_diff >= 1:
                    duration_str = '1 Y'
                else:
                    duration_str = str(years_diff) + ' Y'
                bars = self.ib.reqHistoricalData(c, endDateTime=end_date_time, durationStr=duration_str, barSizeSetting=bar_size_setting, whatToShow=what_to_show, useRTH=True, formatDate=1)
                if len(bars) > 0:
                    bars_list.append(bars)
                    end_date_time = bars[0].date
                else:
                    break
                years_diff -= 1

            if months_diff > 0:
                duration_str = str(months_diff) + ' M'
                bars = self.ib.reqHistoricalData(c, endDateTime=end_date_time, durationStr=duration_str, barSizeSetting=bar_size_setting, whatToShow=what_to_show, useRTH=True, formatDate=1)
                if len(bars) > 0:
                    bars_list.append(bars)
                    end_date_time = bars[0].date
                else:
                    self.logger.warning("No monthly bars fetched for: " + c.symbol)

            while days_diff > 0:
                if days_diff >= 100:
                    duration_str = '100 D'
                else:
                    duration_str = str(days_diff) + ' D'
                bars = self.ib.reqHistoricalData(c, endDateTime=end_date_time, durationStr=duration_str, barSizeSetting=bar_size_setting, whatToShow=what_to_show, useRTH=True, formatDate=1)
                if len(bars) > 0:
                    bars_list.append(bars)
                    end_date_time = bars[0].date
                else:
                    self.logger.warning("No daily bars fetched for: " + c.symbol)
                days_diff -= 100

            while hours_diff > 0:
                secs = hours_diff * 60 * 60
                duration_str = str(secs) + ' S'
                bars = self.ib.reqHistoricalData(c, endDateTime=end_date_time, durationStr=duration_str, barSizeSetting=bar_size_setting, whatToShow=what_to_show, useRTH=True, formatDate=1)
                if len(bars) > 0:
                    bars_list.append(bars)
                    end_date_time = bars[0].date
                else:
                    self.logger.warning("No hourly bars fetched for: " + c.symbol)
                hours_diff -= 24

            
            if len(bars_list) == 0: #if no bars, probably because of no market data permissions.
                self.logger.warning("Empty bars list for contract with symbol " + c.symbol)
            else:         
                bars_ordered_list = [b for bars in reversed(bars_list) for b in bars]
                df = util.df(bars_ordered_list)
                #remove rows in the dataframe that are before the start_date parameter ... can happen because of the way the data is backwards fetched above because of weekends/holidays
                df['date'] = pd.to_datetime(df['date'])
                df['symbol'] = c.symbol + '.' + c.currency
                if df_res is None:
                    df_res = df
                else:
                    df_res = df_res.append(df)

        df_res = df_res.sort_values(by=['symbol', 'date'])
        return df_res


if __name__ == "__main__":
    specs = []
    '''tsla_specs = HistoricalDataSpecs('TSLA', 'SMART', 'USD', contract_stock_type, data_type_trades)
    msft_specs = HistoricalDataSpecs('MSFT', 'SMART', 'USD', contract_stock_type, data_type_trades)
    specs.extend([tsla_specs, msft_specs])
    ib = IBKR(config_file_path='/home/ghelie/fin_app/fin_app_core/data_vendors/IBKR/ibkr_config.json')
    for spec in specs:
        df = ib.get_historical_bar_data(spec, '2019-01-01', '', 1, 'hour', True)
        df.to_csv(spec.ticker + '.csv')'''

    '''ib = IBKR(config_file_path='/home/ghelie/fin_app/fin_app_core/data_vendors/IBKR/ibkr_config.json')
    contract = Contract()
    contract.symbol = "EUR";
    contract.secType = "CASH";
    contract.currency = "USD";
    contract.exchange = "IDEALPRO";'''


    '''specs = HistoricalDataSpecs('USD', 'IDEALPRO', 'JPY', contract_fx_type, data_type_midpoint)
    ib = IBKR(config_file_path='/home/ghelie/fin_app/fin_app_core/data_vendors/IBKR/ibkr_config.json')
    df = ib.get_historical_bar_data(specs, '', '', 1, 'd', True)
    df.to_csv(specs.ticker + '.csv')

    end_date_str = '2021-01-15'
    end_date_obj = datetime.strptime(end_date_str, '%Y-%m-%d')
    bars = ib.ib.reqHistoricalData(contract, endDateTime=end_date_obj, durationStr='12 W', barSizeSetting='1 day', whatToShow='MIDPOINT', useRTH=True, formatDate=1)
    i = 2'''

    contract = Contract()
    contract.symbol = 'AAPL'
    contract.secType = 'STK'
    contract.currency = 'USD'
    contract.exchange = 'SMART'
    ib = IBKR(config_file_path='/home/ghelie/fin_app/fin_app_core/data_vendors/IBKR/ibkr_config.json')
    ret = ib.ib.reqFundamentalData(contract, 'RESC')
    i = 2



        