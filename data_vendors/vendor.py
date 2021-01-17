from abc import ABC, ABCMeta, abstractmethod

contract_stock_type = 1
contract_option_type = 2
contract_fx_type = 3

data_type_trades = 1 # split adjusted
data_type_trades_adjusted = 2 # split and dividend adjusted
data_type_midpoint = 3

bar_size_second = '1 s'
bar_size_minute = '1 m'
bar_size_hour = '1 h'
bar_size_day = '1 d'

class HistoricalDataSpecs:
    def __init__(self, symbol, exchange, currency, contract_type, data_type):
        self.symbol = symbol
        self.exchange = exchange
        self.currency = currency
        self.contract_type = contract_type
        self.data_type = data_type

class Vendor(ABC):
    
    @abstractmethod
    def get_all_companies(**kwargs):
        """ 
            Retrieves all companies supported by registered data vendors

        Raises:
            NotImplementedError: this method is implemented in concrete classes
        """
        raise NotImplementedError("get_all_companies not implemented in base class.")

    @abstractmethod
    def get_fundamental_data(**kwargs):
        """
            Retrieves all fundamental data for all the companies supported by registered data vendors

        Raises:
            NotImplementedError: this method is implemented in concrete classes
        """
        raise NotImplementedError("get_fundamental_data not implemented in base class.")
    
    def validate_get_historical_bar_data(self, retrieval_specs, start_date_obj, end_date_obj, bar_size, bar_size_unit, only_regular_hours):
        if start_date_obj > end_date_obj:
            raise ValueError("End date should come after start date")
        if bar_size_unit != 's' and bar_size_unit != 'secs' and bar_size_unit != 'min' and bar_size_unit != 'minutes' \
           and bar_size_unit != 'hour' and bar_size_unit != 'hours' and bar_size_unit != 'd' and bar_size_unit != 'days':
           raise ValueError("Invalid bar_size_unit value provided. Must be: s/secs, min/minutes, h/hours, d/days")

    @abstractmethod
    def get_historical_bar_data(retrieval_specs, start_date, end_date, bar_size, bar_size_unit, only_regular_hours):
        """
            Retrieves all historical stock prices for a ticker. Specify below parameters to customize retreival

        Args:
            tickers (list str): List of tickers for which historical stock prices will be retrieved
            start_date (str): Retrieve data from this date
            end_date (str): Stop retrieving data after this date
            timeframe (int): timeframe of the bars retrieved in seconds
            time_frame_time_unit (str): unit of time for timeframe (s/secs, min/minutes, h/hours, d/days)
            only_regular_hours (bool): Restricts data to regular market hours or includes after hours if set to False

        Raises:
            NotImplementedError: this method is implemented in concrete classes
        """
        raise NotImplementedError("get_historical_stock_price not implemented in base class.")

    @abstractmethod
    def get_historical_bar_data_full(self, start_date, end_date, bar_size, bar_size_unit, only_regular_hours, data_type, symbols_filtered_in, symbols_filtered_out):
        """
            Retrieves all historical bar data for different types of data (fx, stock, options, etc.)

        Args:
            start_date (str): Retrieve data from this date
            timeframe (int): timeframe of the bars retrieved in seconds
            time_frame_time_unit (str): unit of time for timeframe (s/secs, min/minutes, h/hours, d/days)
            only_regular_hours (bool): Restricts data to regular market hours or includes after hours if set to False

        Raises:
            NotImplementedError: this method is implemented in concrete classes
        """
        raise NotImplementedError("get_historical_stock_price not implemented in base class.")