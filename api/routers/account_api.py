#not an api for now, run as a script

import pandas as pd
import numpy as np
import calendar
import datetime
from db.models import *
from py_common_utils_gh.db_utils.db_utils import SqlAlchemySessionManager
import requests
import re

def match_t5008_with_trade_logs():
    df_t5008 = pd.read_csv('/home/ghelie/taxes/2020/t5008_ibkr.csv')

    df_trade_logs = pd.read_csv('/home/ghelie/taxes/2020/result.csv')

    for idx, row in df_t5008.iterrows():
        df_trade_logs.loc[df_trade_logs['description'] == row['Description'], 'brokerage_reported_proceeds'] = row['Proceeds']
        df_trade_logs.loc[df_trade_logs['description'] == row['Description'], 'brokerage_reported_cost'] = row['Cost']
        df_trade_logs.loc[df_trade_logs['description'] == row['Description'], 'brokerage_reported_capital_gain'] = row['Proceeds'] - row['Cost']

    df_trade_logs.to_csv("/home/ghelie/taxes/2020/result_combined.csv")

def mark_wash_sales():
    tax_year_end = datetime.datetime.strptime('2020-12-31', '%Y-%m-%d').date()

    wash_sale_period_end = datetime.datetime.strptime('2021-1-31', '%Y-%m-%d').date()
    
    '''manager = SqlAlchemySessionManager()
    with manager.session_scope(db_url='postgresql://postgres:navo1234@localhost:5432/fin_app_core_db', template_name='default_session') as session:
        df = pd.read_sql(session.query(AccountTrade).filter(AccountTrade.trade_date <= wash_sale_period_end).statement, session.bind)
        #df = pd.read_sql(session.query(AccountTrade).statement, session.bind)
        #df = df[((df['trade_type'] == trade_type_sell_to_open) | (df['trade_type'] == trade_type_buy_to_open)) & (df['trade_date'] >= datetime.date(2020, 11, 30))]
        df = df[((df['trade_type'] == trade_type_sell_to_open) | (df['trade_type'] == trade_type_buy_to_open)) & (df['trade_date'] >= datetime.date(2020, 11, 30))]
        #df = df.sort_values(['trade_date'])
        #df.to_csv("/home/ghelie/taxes/2020/wash.csv")
        #df = df.replace({np.nan: None})
        #df = df.sort_values(['trade_date']).groupby('symbol')'''


def save_account_trades_questrade():
    start_date = '2020-01-01T00:00:00-00:00'
    #end_date = '2020-12-31T00:00:00-00:00'

    start_date = datetime.date(2020, 1, 1)
    #print(start_date.strftime('%Y-%m-%dT%H:%M:%S.%f%z'))

    trade_logs_df = pd.DataFrame(columns=['trade_date', 'action', 'symbol', 'description', 'currency', 'quantity', 'price', 'grossAmount', 'commission', 'netAmount'])

    '''while start_date.year != 2021:
        nb_days_in_mo = calendar.monthrange(start_date.year, start_date.month)[1]
        end_date = datetime.date(start_date.year, start_date.month, nb_days_in_mo)
        start_date_str = start_date.strftime('%Y-%m-%dT%H:%M:%S-00:00')
        end_date_str = end_date.strftime('%Y-%m-%dT%H:%M:%S-00:00')

        url = 'https://api01.iq.questrade.com/v1/accounts/27261142/activities'
        url += '?' + 'startTime=' + start_date_str + '&' + 'endTime=' + end_date_str
        headers = {"Authorization": "Bearer sJt2Sswa1NAtAel2sn0TNQ6TmzfpUKb60"}
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            r = r.json()
            for activity in r['activities']:            
                if activity['type'] == 'Trades' and len(activity['symbol']) > 0:
                    trade_date = activity['tradeDate'].split('T')[0]
                    trade_date = datetime.datetime.strptime(trade_date, '%Y-%m-%d').date()
                    new_row = [trade_date, activity['action'], activity['symbol'], activity['description'], activity['currency'], activity['quantity'], activity['price'], activity['grossAmount'], \
                               activity['commission'], activity['netAmount']]
                    trade_logs_df = trade_logs_df.append(pd.Series(new_row, index=trade_logs_df.columns[:len(new_row)]), ignore_index=True)

      
        start_date = next_month = datetime.date(start_date.year + int(start_date.month / 12), ((start_date.month % 12) + 1), 1)

    trade_logs_df.to_csv("/home/ghelie/taxes/2020/questrade_result.csv")'''

    df = pd.read_csv("/home/ghelie/taxes/2020/questrade_result.csv")
    df = df.replace({np.nan: None})
    df = df.sort_values(['trade_date']).groupby('symbol')

    manager = SqlAlchemySessionManager()
    with manager.session_scope(db_url='postgresql://postgres:navo1234@localhost:5432/fin_app_core_db', template_name='default_session') as session:
        for symbol, group_data in df:
            grp_initial_trade_type = None
            for idx, row in group_data.iterrows():
                if grp_initial_trade_type == None:
                    if row['action'] == 'Buy':
                        grp_initial_trade_type = trade_type_buy_to_open
                    else:
                        grp_initial_trade_type = trade_type_sell_to_open

                trade_date = datetime.datetime.strptime(row['trade_date'], '%Y-%m-%d').date()
                current_trade_type = None
                if row['action'] == 'Buy' and grp_initial_trade_type == trade_type_buy_to_open:
                    current_trade_type = trade_type_buy_to_open
                elif row['action'] == 'Buy' and grp_initial_trade_type == trade_type_sell_to_open:
                    current_trade_type = trade_type_buy_to_close
                elif row['action'] == 'Sell' and grp_initial_trade_type == trade_type_buy_to_open:
                    current_trade_type = trade_type_sell_to_close
                elif row['action'] == 'Sell' and grp_initial_trade_type == trade_type_sell_to_open:
                    current_trade_type = trade_type_sell_to_open

                is_option_trade = True
                is_call = None
                desc_tokens = row['description'].split()
                if 'PUT' in desc_tokens:
                    is_call = False
                elif 'CALL' in desc_tokens:
                    is_call = True
                else:
                    is_option_trade = False

                expiry = None
                create_expire_buy_to_close_trade = False
                create_expire_sell_to_close_trade = False
                date_exp_virtual_trade = None
                if symbol == 'ZM21Aug20P150.00':
                    i = 2
                if is_option_trade and (current_trade_type == trade_type_sell_to_open or current_trade_type == trade_type_buy_to_open):
                    date_exp = datetime.datetime.strptime(desc_tokens[2], '%m/%d/%y').date()
                    date_exp_virtual_trade = date_exp
                    if date_exp < datetime.date(2020, 12, 31):
                        if current_trade_type == trade_type_sell_to_open:
                            offset_df = group_data[group_data['action'] == 'Buy']
                            if offset_df.shape[0] == 0:
                                create_expire_buy_to_close_trade = True
                        if current_trade_type == trade_type_buy_to_open:
                            offset_df = group_data[group_data['action'] == 'Sell']
                            if offset_df.shape[0] == 0:
                                create_expire_sell_to_close_trade = True

                    '''if group_data.shape[0] == 1 and date_exp < datetime.date(2020, 12, 31) and current_trade_type == trade_type_sell_to_open:
                        create_expire_buy_to_close_trade = True
                    elif group_data.shape[0] == 1 and date_exp < datetime.date(2020, 12, 31) and current_trade_type == trade_type_buy_to_open:
                        create_expire_sell_to_close_trade = True'''


                quantity = abs(row['quantity'])
                #commission = abs(row['IBCommission']) commissions can be positive for ibkr ..
                commission = row['commission']
                multiplier = 1
                if is_option_trade:
                    multiplier = 100
                asset_class = 'STK'
                if is_option_trade:
                    asset_class = 'OPT'
                underlying_symbol = row['symbol']
                if is_option_trade:
                    underlying_symbol = desc_tokens[1]
                trade = AccountTrade(currency=row['currency'], fx_rate_to_base=1.3415, asset_class=asset_class, underlying_symbol=underlying_symbol, symbol=row['symbol'], \
                                    description=row['description'], trade_date=trade_date, trade_type=current_trade_type, quantity=quantity, strike=None, is_call=is_call, expiry=None, \
                                    multiplier=multiplier, trade_price=row['price'], commission=commission, commission_currency=commission, cost_basis=0, \
                                    proceeds=0, brokerage_id=questrade_brokerage_id)


                trade_expire_buy_to_close = None
                if create_expire_buy_to_close_trade:
                    trade_expire_buy_to_close = AccountTrade(currency=row['currency'], fx_rate_to_base=1.3415, asset_class=asset_class, underlying_symbol=underlying_symbol, symbol=row['symbol'], \
                                        description=row['description'], trade_date=date_exp_virtual_trade, trade_type=trade_type_buy_to_close, quantity=quantity, strike=None, is_call=is_call, expiry=None, \
                                        multiplier=multiplier, trade_price=0, commission=0, commission_currency=0, cost_basis=0, \
                                        proceeds=0, brokerage_id=questrade_brokerage_id)

                trade_expire_sell_to_close = None
                if create_expire_sell_to_close_trade:
                    trade_expire_sell_to_close = AccountTrade(currency=row['currency'], fx_rate_to_base=1.3415, asset_class=asset_class, underlying_symbol=underlying_symbol, symbol=row['symbol'], \
                                        description=row['description'], trade_date=date_exp_virtual_trade, trade_type=trade_type_sell_to_close, quantity=quantity, strike=None, is_call=is_call, expiry=None, \
                                        multiplier=multiplier, trade_price=0, commission=0, commission_currency=0, cost_basis=0, \
                                        proceeds=0, brokerage_id=questrade_brokerage_id)

                session.add(trade)
                if trade_expire_buy_to_close is not None:
                    session.add(trade_expire_buy_to_close)
                if trade_expire_sell_to_close is not None:
                    session.add(trade_expire_sell_to_close)
                session.commit()

def save_account_trades_ibkr():
    avg_tax_rates = {'USD': 1.3415}

    base_currency = 'CAD'

    tax_year_end = datetime.datetime.strptime('2020-12-31', '%Y-%m-%d').date()


    ibkr_trade_logs_file_path = "/home/ghelie/taxes/2020/ibkr_final.csv"

    ibkr_trade_logs_df = pd.read_csv(ibkr_trade_logs_file_path)
    ibkr_trade_logs_df = ibkr_trade_logs_df.replace({np.nan: None})
    ibkr_trade_logs_df = ibkr_trade_logs_df.sort_values(['TradeDate']).groupby('Symbol')

    open_transactions = []

    #assumes that there were no transactions made prior to this

    manager = SqlAlchemySessionManager()
    with manager.session_scope(db_url='postgresql://postgres:navo1234@localhost:5432/fin_app_core_db', template_name='default_session') as session:
        for symbol, group_data in ibkr_trade_logs_df:
            grp_initial_trade_type = None
            for idx, row in group_data.iterrows():
                if row['AssetClass'] == 'CASH':
                    continue
                if grp_initial_trade_type == None:
                    if row['Buy/Sell'] == 'BUY':
                        grp_initial_trade_type = trade_type_buy_to_open
                    else:
                        grp_initial_trade_type = trade_type_sell_to_open

                trade_date = datetime.datetime.strptime(row['TradeDate'], '%Y-%m-%d').date()
                current_trade_type = None
                if row['Buy/Sell'] == 'BUY' and grp_initial_trade_type == trade_type_buy_to_open:
                    current_trade_type = trade_type_buy_to_open
                elif row['Buy/Sell'] == 'BUY' and grp_initial_trade_type == trade_type_sell_to_open:
                    current_trade_type = trade_type_buy_to_close
                elif row['Buy/Sell'] == 'SELL' and grp_initial_trade_type == trade_type_buy_to_open:
                    current_trade_type = trade_type_sell_to_close
                elif row['Buy/Sell'] == 'SELL' and grp_initial_trade_type == trade_type_sell_to_open:
                    current_trade_type = trade_type_sell_to_open

                is_call = None
                if row['Put/Call'] == 'P':
                    is_call = False
                elif row['Put/Call'] == 'C':
                    is_call = True

                symbol = row['Symbol']
                if is_call is not None:
                    desc_tokens = row['Description'].split()
                    first_letter_of_mo_idx = 0
                    for idx, x in enumerate(desc_tokens[1]):
                        if not x.isdigit():
                            first_letter_of_mo_idx = idx
                            break
                    
                    day = desc_tokens[1][:idx]
                    if day[0] == '0':
                        day = day[1:]
                    mo = desc_tokens[1][idx:]
                    mo = mo.capitalize()
                    desc_tokens[1] = day + mo
                    
                    symbol = desc_tokens[0] + desc_tokens[1] + desc_tokens[3] + desc_tokens[2]

                quantity = abs(row['Quantity'])
                cost_basis = abs(row['CostBasis'])
                proceeds = abs(row['Proceeds'])
                #commission = abs(row['IBCommission']) commissions can be positive for ibkr ..
                commission = row['IBCommission']
                trade = AccountTrade(currency=row['CurrencyPrimary'], fx_rate_to_base=row['FXRateToBase'], asset_class=row['AssetClass'], underlying_symbol=row['UnderlyingSymbol'], symbol=symbol, \
                                    description=row['Description'], trade_date=trade_date, trade_type=current_trade_type, quantity=quantity, strike=row['Strike'], is_call=is_call, expiry=row['Expiry'], \
                                    multiplier=row['Multiplier'], trade_price=row['TradePrice'], commission=commission, commission_currency=row['IBCommissionCurrency'], cost_basis=cost_basis, \
                                    proceeds=proceeds, brokerage_id=ibkr_brokerage_id)
                session.add(trade)
                session.commit()

def generate_tax_report():
    tax_year_end = datetime.datetime.strptime('2020-12-31', '%Y-%m-%d').date()

    avg_fx_rate = 1.3415

    out_df = pd.DataFrame(columns=['brokerage', 'date', 'account_base_currency', 'currency', 'tax_year_average_fx_rate', \
                                   'asset_class', 'quantity_closed', 'description', 'brokerage_reported_cost', \
                                   'trade_logs_cost', 'trade_logs_cost_base_currency', 'trade_logs_cost_base_currency_avg_fx_rate', \
                                   'brokerage_reported_proceeds',  \
                                   'trade_logs_proceeds', 'trade_logs_proceeds_base_currency', 'trade_logs_proceeds_base_currency_avg_fx_rate', \
                                   'brokerage_reported_capital_gain', 'trade_logs_reported_capital_gain', 'brokerage_reported_capital_gain_base_currency', 'trade_logs_reported_capital_gain_base_currency_avg_fx_rate'])

    manager = SqlAlchemySessionManager()
    with manager.session_scope(db_url='postgresql://postgres:navo1234@localhost:5432/fin_app_core_db', template_name='default_session') as session:
        df = pd.read_sql(session.query(AccountTrade).filter(AccountTrade.trade_date <= tax_year_end).statement, session.bind)
        df = df.replace({np.nan: None})
        df = df.sort_values(['trade_date']).groupby('symbol')
        for symbol, group_data in df:
            total_cost = 0
            total_cost_base_currency = 0
            total_cost_base_currency_avg_fx_rate = 0
            total_proceeds = 0
            total_proceeds_base_currency = 0
            total_proceeds_base_currency_avg_fx_rate = 0
            initial_trade_type = group_data.iloc[0]['trade_type']
            asset_class = group_data.iloc[0]['asset_class']
            desc = group_data.iloc[0]['description']

            group_data.loc[((group_data['trade_type'] == trade_type_buy_to_open) | (group_data['trade_type'] == trade_type_buy_to_close)) & (group_data['commission'] >= 0) \
                            , 'total_trade_price'] = group_data['trade_price'] * group_data['quantity'] * group_data['multiplier'] - group_data['commission']

            group_data.loc[((group_data['trade_type'] == trade_type_buy_to_open) | (group_data['trade_type'] == trade_type_buy_to_close)) & (group_data['commission'] < 0) \
                            , 'total_trade_price'] = group_data['trade_price'] * group_data['quantity'] * group_data['multiplier'] - group_data['commission']

            group_data.loc[((group_data['trade_type'] == trade_type_sell_to_open) | (group_data['trade_type'] == trade_type_sell_to_close)) & (group_data['commission'] >= 0) \
                            , 'total_trade_price'] = group_data['trade_price'] * group_data['quantity'] * group_data['multiplier'] + group_data['commission']
            
            group_data.loc[((group_data['trade_type'] == trade_type_sell_to_open) | (group_data['trade_type'] == trade_type_sell_to_close)) & (group_data['commission'] < 0) \
                            , 'total_trade_price'] = group_data['trade_price'] * group_data['quantity'] * group_data['multiplier'] + group_data['commission']

            group_data['total_trade_price_base_currency'] = group_data['total_trade_price'] * group_data['fx_rate_to_base']
            group_data['total_trade_price_base_currency_avg_fx_rate'] = group_data['total_trade_price'] * avg_fx_rate

            print(symbol)
            df_cpy = group_data[(group_data['trade_type'] == trade_type_buy_to_open) | (group_data['trade_type'] == trade_type_buy_to_close)]
            qty_cost = df_cpy['quantity'].sum()
            total_cost = df_cpy['total_trade_price'].sum()
            total_cost_base_currency = df_cpy['total_trade_price_base_currency'].sum()
            total_cost_base_currency_avg_fx_rate = df_cpy['total_trade_price_base_currency_avg_fx_rate'].sum()
            acb = total_cost / qty_cost
            acb_base_currency = total_cost_base_currency / qty_cost
            acb_base_currency_avg_fx_rate = total_cost_base_currency_avg_fx_rate / qty_cost

            df_cpy = group_data[(group_data['trade_type'] == trade_type_sell_to_close) | (group_data['trade_type'] == trade_type_sell_to_open)]
            #print(df_cpy[['quantity', 'trade_price', 'total_trade_price', 'commission']])
            qty_proceeds = df_cpy['quantity'].sum()
            #qty_closed = df_cpy['quantity'].sum()
            total_proceeds = df_cpy['total_trade_price'].sum()
            total_proceeds_base_currency = df_cpy['total_trade_price_base_currency'].sum()
            total_proceeds_base_currency_avg_fx_rate = df_cpy['total_trade_price_base_currency_avg_fx_rate'].sum()

            cap_gains = total_proceeds - (qty_proceeds * acb)
            cap_gains_base_currency = total_proceeds_base_currency - (qty_proceeds * acb_base_currency)
            cap_gains_base_currency_avg_fx_rate = total_proceeds_base_currency_avg_fx_rate - (qty_proceeds * acb_base_currency_avg_fx_rate)

            df_cpy = group_data[(group_data['trade_type'] == trade_type_sell_to_close) | (group_data['trade_type'] == trade_type_buy_to_close)].sum()
            qty_closed = df_cpy['quantity'].sum()

            brokerage = group_data.iloc[0]['brokerage_id']
            if brokerage == ibkr_brokerage_id:
                brokerage = 'Interactive Brokers'
            elif brokerage == questrade_brokerage_id:
                brokerage = 'Questrade'
            
        #res = session.query(AccountTrade).filter(AccountTrade.trade_date <= tax_year_end).all()
            new_row = [brokerage, None, 'CAD', group_data.iloc[0]['currency'], avg_fx_rate, asset_class, qty_closed, desc, None, total_cost, \
                       total_cost_base_currency, total_cost_base_currency_avg_fx_rate, None, total_proceeds, total_proceeds_base_currency, total_proceeds_base_currency_avg_fx_rate, None, \
                       cap_gains, cap_gains_base_currency, cap_gains_base_currency_avg_fx_rate ]
            out_df = out_df.append(pd.Series(new_row, index=out_df.columns[:len(new_row)]), ignore_index=True)
            #out_df.loc[len(out_df)] = new_row

        out_df.to_csv("/home/ghelie/taxes/2020/result.csv")

if __name__ == "__main__":
    #save_account_trades_ibkr()
    generate_tax_report()
    #match_t5008_with_trade_logs()
    #mark_wash_sales()
    #save_account_trades_questrade()