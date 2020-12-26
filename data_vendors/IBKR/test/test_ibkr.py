from data_vendors.IBKR.ibkr import *
from datetime import datetime
import os
from data_vendors.vendor import *
import pytest


def test_ib_historical_data(caplog):
    __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    test_config_file_path = os.path.join(__location__, 'test_ibkr_config.json')
    ib = IBKR(config_file_path=test_config_file_path)

    tsla_specs = HistoricalDataSpecs('TSLA', 'SMART', 'USD', contract_stock_type, data_type_trades)
    msft_specs = HistoricalDataSpecs('MSFT', 'SMART', 'USD', contract_stock_type, data_type_trades)
    df = ib.get_historical_bar_data(tsla_specs, '2019-01-01', '', 1, 'hour', True)
    rows = df.iloc[[0, -1]]
    assert rows.iloc[0]['date'].to_pydatetime().replace(tzinfo=None) == datetime(2019, 1, 2, 9, 30) #2019-01-01 is a holiday
    last_date = rows.iloc[1]['date'].to_pydatetime().replace(tzinfo=None)
    now = datetime.now().replace(tzinfo=None)
    assert last_date.year == now.year
    assert last_date.month == now.month
    assert last_date.day == now.day

    df = ib.get_historical_bar_data(msft_specs, '2019-01-02', '2019-01-03', 1, 'hour', True)
    rows = df.iloc[[0, -1]]
    assert rows.iloc[0]['date'].to_pydatetime().replace(tzinfo=None) == datetime(2019, 1, 2, 9, 30)
    assert rows.iloc[1]['date'].to_pydatetime().replace(tzinfo=None) == datetime(2019, 1, 2, 15, 0)
    assert df.shape[0] == 7

    with pytest.raises(ValueError):
        df = ib.get_historical_bar_data(msft_specs, 's', '2019-01-04', 1, 'hour', True)

    caplog.records.clear()
    unknown_specs = HistoricalDataSpecs('blabla', 'SMART', 'USD', contract_stock_type, data_type_trades)
    df = ib.get_historical_bar_data(unknown_specs, '2019-01-01', '', 1, 'hour', True)
    assert len(caplog.records) > 0
    assert df.empty
    for record in caplog.records:
        if record.name == 'ibkr_logger':
            assert record.levelname == 'WARNING'
            assert record.message == "Failed to qualify contract with ticker: blabla for vendor IBKR."

