from data_vendors.IBKR.ibkr import *
from datetime import datetime
import os
from data_vendors.vendor import *
import pytest


def test_ib_historical_data(caplog):
    __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    test_config_file_path = os.path.join(__location__, 'test_ibkr_config.json')
    ib = IBKR(config_file_path=test_config_file_path)

    df = ib.get_historical_bar_data('2019-01-01', '2019-10-10', 1, 'd', True, data_type_fx)