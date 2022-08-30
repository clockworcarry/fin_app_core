#not an api for now, run as a script

from http.client import FOUND
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
    #start_date = '2021-01-01T00:00:00-00:00'
    #end_date = '2020-12-31T00:00:00-00:00'

    start_date = datetime.date(2020, 1, 1)
    #print(start_date.strftime('%Y-%m-%dT%H:%M:%S.%f%z'))

    while start_date.year != 2022:
        nb_days_in_mo = calendar.monthrange(start_date.year, start_date.month)[1]
        end_date = datetime.date(start_date.year, start_date.month, nb_days_in_mo)
        start_date_str = start_date.strftime('%Y-%m-%dT%H:%M:%S-00:00')
        end_date_str = end_date.strftime('%Y-%m-%dT%H:%M:%S-00:00')

        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url='postgresql://postgres:navo1234@localhost:5432/fin_app_core_db', template_name='default_session') as session:
            url = 'https://api05.iq.questrade.com/v1/accounts/27261142/activities'
            url += '?' + 'startTime=' + start_date_str + '&' + 'endTime=' + end_date_str
            headers = {"Authorization": "Bearer ddOtrG5eAc_pYzT9Lq_3yIzM-HX5AuAl0"}
            r = requests.get(url, headers=headers)
            if r.status_code == 200:
                r = r.json()
                for activity in r['activities']:         
                    if ((activity['type'] == 'Trades' or (activity['type'] == 'Other' and activity['action'] == 'ASN') or (activity['type'] == 'Other' and activity['action'] == 'EXP')) and len(activity['symbol'])) > 0:
                        trade_date = activity['tradeDate'].split('T')[0]
                        trade_date = datetime.datetime.strptime(trade_date, '%Y-%m-%d').date()
                        
                        trade_type = 0
                        if activity['action'] == 'Buy':
                            trade_type = trade_type_buy
                        elif activity['action'] == 'Sell':
                            trade_type = trade_type_sell
                        elif activity['action'] == 'ASN':
                            trade_type = trade_type_assigment
                        elif activity['action'] == 'EXP':
                            trade_type = trade_type_expiration

                        desc_tokens = activity['description'].split()

                        asset_class = 'STK'
                        if 'PUT' in activity['description'] or 'CALL' in activity['description']:
                            asset_class = 'OPT'
                        
                        underlying_symbol = activity['symbol']
                        if asset_class == 'OPT':
                            underlying_symbol = desc_tokens[1]

                        multiplier = 1
                        if asset_class == 'OPT':
                            multiplier = 100
                        
                        trade = AccountTrade(fx_rate_to_base=0, currency=activity['currency'], asset_class=asset_class, underlying_symbol=underlying_symbol, symbol=activity['symbol'], \
                                        description=activity['description'], trade_date=trade_date, trade_type=trade_type, quantity=activity['quantity'], strike=None, is_call=False, expiry=None, \
                                        multiplier=multiplier, trade_price=activity['price'], commission=activity['commission'], commission_currency=activity['currency'], cost_basis=0, \
                                        proceeds=0, brokerage_id=questrade_brokerage_id)
                        session.add(trade)
                        session.commit()
            
            start_date = next_month = datetime.date(start_date.year + int(start_date.month / 12), ((start_date.month % 12) + 1), 1)

def save_account_trades_ibkr():
    ibkr_trade_logs_file_path = "/home/ghelie/taxes/2021/ibkr_trade_logs_2021.csv"

    ibkr_trade_logs_df = pd.read_csv(ibkr_trade_logs_file_path)
    ibkr_trade_logs_df = ibkr_trade_logs_df.replace({np.nan: None})
    ibkr_trade_logs_df = ibkr_trade_logs_df.sort_values(['TradeDate'])

    open_transactions = []

    #assumes that there were no transactions made prior to this

    manager = SqlAlchemySessionManager()
    with manager.session_scope(db_url='postgresql://postgres:navo1234@localhost:5432/fin_app_core_db', template_name='default_session') as session:
        for idx, row in ibkr_trade_logs_df.iterrows():
            symbol = row['Symbol']
            if row['AssetClass'] == 'OPT':
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
            
            trade_type = trade_type_buy
            if row['Buy/Sell'] == 'SELL':
                trade_type = trade_type_sell

            underlying_symbol = row['UnderlyingSymbol']
            if underlying_symbol == None:
                underlying_symbol = symbol

            trade = AccountTrade(currency=row['CurrencyPrimary'], fx_rate_to_base=row['FXRateToBase'], asset_class=row['AssetClass'], underlying_symbol=underlying_symbol, symbol=symbol, \
                                    description=row['Description'], trade_date=row['TradeDate'], trade_type=trade_type, quantity=row['Quantity'], strike=None, is_call=False, expiry=None, \
                                    multiplier=row['Multiplier'], trade_price=row['TradePrice'], commission=row['IBCommission'], commission_currency=row['IBCommissionCurrency'], cost_basis=0, \
                                    proceeds=0, brokerage_id=ibkr_brokerage_id)
            session.add(trade)
            session.commit()

class TradeGroup:
    def __init__(self):
        self.asset_class = ''
        self.underlying_symbol = ''
        self.symbol = ''
        self.trades = []
        self.is_fully_closed = False
        self.is_partially_closed = False
        self.is_fully_open = False
        self.qty_opened = 0
        self.qty_open = 0
        self.qty_closed = 0
        self.cost_basis = 0
        self.taxes = []

class TaxCurrency:
    def __init__(self):
        self.currency = ''
        self.fx_rate_to_base = 1

class TaxContextYear:
    def __init__(self):
        self.currencies = []
        self.year = 0

class TaxContext:
    def __init__(self):
        self.base_currency = ''
        self.years = []

class Tax:
    def __init__(self, tax_due, tax_due_base_currency , tax_proceeds, tax_proceeds_base_currency, tax_costs, tax_costs_base_currency, deductibles):
        self.tax_due = tax_due
        self.tax_due_base_currency = tax_due_base_currency
        self.tax_proceeds = tax_proceeds
        self.tax_proceeds_base_currency = tax_proceeds_base_currency
        self.tax_costs = tax_costs
        self.tax_costs_base_currency = tax_costs_base_currency
        self.deductibles = deductibles
        self.year = 0


def group_trades(trades):
    grouped_trades = []
    
    for t in trades:
        found = False
        for g_t in grouped_trades:
            if t.asset_class == g_t.asset_class and t.underlying_symbol == g_t.underlying_symbol and t.symbol == g_t.symbol:
                g_t.trades.append(t)
                found = True
                break
        if not found:
            new_grouped_trade = TradeGroup()
            new_grouped_trade.asset_class = t.asset_class
            new_grouped_trade.underlying_symbol = t.underlying_symbol
            new_grouped_trade.symbol = t.symbol
            if t.trade_type == trade_type_buy_to_open or t.trade_type == trade_type_sell_to_open:                
                new_grouped_trade.qty_opened += t.quantity
            elif t.trade_type == trade_type_buy_to_close or t.trade_type == trade_type_sell_to_close:
                new_grouped_trade.qty_closed += t.quantity
            new_grouped_trade.trades.append(t)
            grouped_trades.append(new_grouped_trade)
    
    return grouped_trades

def parse_trades(group_trades):
    for t_g in group_trades:
        t_g.trades = t_g.sort(key=lambda x: x.trade_date, reverse=False)
        for t in t_g.trades:
           pass 



def get_trade_group_qty_open(trade_group):
    qty_open = 0
    for t in trade_group.trades:
        if t.trade_type == trade_type_buy_to_open or t.trade_type == trade_type_sell_to_open:
            qty_open += t.quantity
        elif t.trade_type == trade_type_buy_to_close or t.trade_type == trade_type_sell_to_close:
            qty_open -= t.quantity
    
    return qty_open



def get_trade_group_qty_closed(trade_group, year):
    qty_closed = 0
    for t in trade_group.trades:
        if t.trade_date.year == year and (t.trade_type == trade_type_buy_to_close or t.trade_type == trade_type_sell_to_close):
            qty_closed += t.quantity
    
    return qty_closed



def get_trade_group_qty_opened(trade_group, year):
    qty_closed = 0
    for t in trade_group.trades:
        if t.trade_date.year == year and (t.trade_type == trade_type_buy_to_close or t.trade_type == trade_type_sell_to_close):
            qty_closed += t.quantity
    
    return qty_closed



def get_trade_group_proceeds(fx_rate_to_base, trade_group, year):
    total_proceeds = 0
    for t in trade_group.trades:
        if t.trade_date.year == year and (t.trade_type == trade_type_buy_to_close or t.trade_type == trade_type_sell_to_close):
            total_proceeds += t.quantity * t.trade_price * t.multiplier * fx_rate_to_base - t.commission 
    return total_proceeds



def get_fx_rate_to_base(trade_ctx, currency, year):
    for yr in trade_ctx.years:
        if yr.year == year:
            for c in yr.currencies:
                if c.currency == currency:
                    return c.fx_rate_to_base
    return 0



def get_trade_group_cost_basis(fx_rate_to_base, trade_group, year):
    qty_open = 0
    total_cost = 0
    cost_basis = 0
    #bought 20 shares: cost_basis = ((200 - 75 - 35) * 17.53 + (20 * 8 + 5)) / 110 = (1577.7 + 165) / 110 = 15.84
    for t in trade_group.trades:
        if t.trade_date.year <= year and (t.trade_type == trade_type_buy_to_open or t.trade_type == trade_type_sell_to_open):
            if cost_basis == 0:
                cost_basis = round((t.quantity * float(t.trade_price) * t.multiplier + float(t.commission)) / t.quantity, 2)
            else:
                cost_basis = round((qty_open * cost_basis + (t.quantity * float(t.trade_price) * t.multiplier + float(t.commission))) / (qty_open + t.quantity), 2)
            qty_open += t.quantity

        elif t.trade_date.year <= year and (t.trade_type == trade_type_buy_to_close or t.trade_type == trade_type_sell_to_close):
            qty_open -= t.quantity

    trade_group.qty_open = qty_open

    return round(cost_basis * fx_rate_to_base, 2)


def get_trade_group_tax(trade_ctx, trade_group, year):
    total_proceeds = 0
    total_cost = 0
    
    if len(trade_group.trades) == 0:
        raise Exception("No trades in group.")
    
    fx_rate_to_base = get_fx_rate_to_base(trade_ctx, trade_group.trades[0].currency, year)
    if fx_rate_to_base == 0:
        raise Exception("Cant find fx rate to base")
    
    cost_basis = get_trade_group_cost_basis(1, trade_group, year)
    cost_basis_base = get_trade_group_cost_basis(fx_rate_to_base, trade_group, year)
    
    for t in trade_group.trades:
        if t.trade_date.year == year and (t.trade_type == trade_type_buy_to_close or t.trade_type == trade_type_sell_to_close):
            total_proceeds += round((t.quantity * float(t.trade_price) * t.multiplier - float(t.commission)), 2)
            total_cost += round(t.quantity * cost_basis, 2)

    tax_due = total_proceeds - total_cost
    if trade_group.qty_open < 0:
       tax_due = -tax_due 
    
    tax = Tax(tax_due, (total_proceeds - total_cost) * fx_rate_to_base,  total_proceeds, total_proceeds * fx_rate_to_base,  total_cost, total_cost * fx_rate_to_base, 0)
    trade_group.taxes.append(tax)
    return tax


def calculate_taxes(trade_ctx, trade_groups, year_start, year_end):
    taxes = []
    for yr in range(year_start, year_end):
        tax = Tax(0, 0, 0, 0, 0, 0, 0)
        tax.year = yr
        for g_t in trade_groups:
            grp_tax = get_trade_group_tax(trade_ctx, g_t, yr)
            tax.tax_due += grp_tax.tax_due
            tax.tax_due_base_currency += grp_tax.tax_due_base_currency
            tax.tax_proceeds += grp_tax.tax_proceeds
            tax.tax_proceeds_base_currency += grp_tax.tax_proceeds_base_currency
            tax.tax_costs += grp_tax.tax_costs
            tax.tax_costs_base_currency += grp_tax.tax_costs_base_currency
        taxes.append(tax)
    
    return taxes



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


def test():
    trades = []

    #ZM long
    acc_trade_one = AccountTrade()
    acc_trade_one.asset_class = 'STK'
    acc_trade_one.symbol = 'CODX'
    acc_trade_one.underlying_symbol = 'CODX'
    acc_trade_one.quantity = 200
    acc_trade_one.trade_price = 17.5
    acc_trade_one.currency = 'USD'
    acc_trade_one.commission = 6.95
    acc_trade_one.multiplier = 1
    acc_trade_one.trade_type = trade_type_buy_to_open
    acc_trade_one.trade_date = datetime.date(2020, 6, 23)

    acc_trade_two = AccountTrade()
    acc_trade_two.asset_class = 'STK'
    acc_trade_two.symbol = 'CODX'
    acc_trade_two.underlying_symbol = 'CODX'
    acc_trade_two.quantity = 75
    acc_trade_two.trade_price = 13.2
    acc_trade_two.currency = 'USD'
    acc_trade_two.commission = 8.3
    acc_trade_two.multiplier = 1
    acc_trade_two.trade_type = trade_type_sell_to_close
    acc_trade_two.trade_date = datetime.date(2020, 9, 21)

    acc_trade_three = AccountTrade()
    acc_trade_three.asset_class = 'STK'
    acc_trade_three.symbol = 'CODX'
    acc_trade_three.underlying_symbol = 'CODX'
    acc_trade_three.quantity = 35
    acc_trade_three.trade_price = 20
    acc_trade_three.currency = 'USD'
    acc_trade_three.commission = 5
    acc_trade_three.multiplier = 1
    acc_trade_three.trade_type = trade_type_sell_to_close
    acc_trade_three.trade_date = datetime.date(2021, 3, 5)

    acc_trade_four = AccountTrade()
    acc_trade_four.asset_class = 'STK'
    acc_trade_four.symbol = 'CODX'
    acc_trade_four.underlying_symbol = 'CODX'
    acc_trade_four.quantity = 20
    acc_trade_four.trade_price = 8
    acc_trade_four.currency = 'USD'
    acc_trade_four.commission = 5
    acc_trade_four.multiplier = 1
    acc_trade_four.trade_type = trade_type_buy_to_open
    acc_trade_four.trade_date = datetime.date(2021, 10, 5)

    acc_trade_five = AccountTrade()
    acc_trade_five.asset_class = 'STK'
    acc_trade_five.symbol = 'CODX'
    acc_trade_five.underlying_symbol = 'CODX'
    acc_trade_five.quantity = 110
    acc_trade_five.trade_price = 34
    acc_trade_five.currency = 'USD'
    acc_trade_five.commission = 7.95
    acc_trade_five.multiplier = 1
    acc_trade_five.trade_type = trade_type_sell_to_close
    acc_trade_five.trade_date = datetime.date(2022, 3, 5)


    #zm short stock
    acc_trade_twelve = AccountTrade()
    acc_trade_twelve.asset_class = 'STK'
    acc_trade_twelve.symbol = 'ZM'
    acc_trade_twelve.underlying_symbol = 'ZM'
    acc_trade_twelve.quantity = 25
    acc_trade_twelve.trade_price = 400
    acc_trade_twelve.currency = 'USD'
    acc_trade_twelve.commission = 6.75
    acc_trade_twelve.multiplier = 1
    acc_trade_twelve.trade_type = trade_type_sell_to_open
    acc_trade_twelve.trade_date = datetime.date(2020, 3, 5)

    acc_trade_13 = AccountTrade()
    acc_trade_13.asset_class = 'STK'
    acc_trade_13.symbol = 'ZM'
    acc_trade_13.underlying_symbol = 'ZM'
    acc_trade_13.quantity = 10
    acc_trade_13.trade_price = 300
    acc_trade_13.currency = 'USD'
    acc_trade_13.commission = 7
    acc_trade_13.multiplier = 1
    acc_trade_13.trade_type = trade_type_buy_to_close
    acc_trade_13.trade_date = datetime.date(2021, 4, 5)

    acc_trade_14 = AccountTrade()
    acc_trade_14.asset_class = 'STK'
    acc_trade_14.symbol = 'ZM'
    acc_trade_14.underlying_symbol = 'ZM'
    acc_trade_14.quantity = 25 #go from short to long
    acc_trade_14.trade_price = 200
    acc_trade_14.currency = 'USD'
    acc_trade_14.commission = 10
    acc_trade_14.multiplier = 1
    acc_trade_14.trade_type = trade_type_buy_to_close
    acc_trade_14.trade_date = datetime.date(2021, 5, 5)

    acc_trade_15 = AccountTrade()
    acc_trade_15.asset_class = 'STK'
    acc_trade_15.symbol = 'ZM'
    acc_trade_15.underlying_symbol = 'ZM'
    acc_trade_15.quantity = 10 
    acc_trade_15.trade_price = 500
    acc_trade_15.currency = 'USD'
    acc_trade_15.commission = 6
    acc_trade_15.multiplier = 1
    acc_trade_15.trade_type = trade_type_sell_to_close
    acc_trade_15.trade_date = datetime.date(2023, 5, 5)


    #zm long opt
    acc_trade_six = AccountTrade()
    acc_trade_six.asset_class = 'OPT'
    acc_trade_six.symbol = 'ZM1May20P133.0'
    acc_trade_six.underlying_symbol = 'ZM'
    acc_trade_six.quantity = 3
    acc_trade_six.trade_price = 2.23
    acc_trade_six.currency = 'USD'
    acc_trade_six.commission = 10
    acc_trade_six.multiplier = 100
    acc_trade_six.trade_type = trade_type_buy_to_open
    acc_trade_six.trade_date = datetime.date(2020, 1, 5) 

    acc_trade_seven = AccountTrade()
    acc_trade_seven.asset_class = 'OPT'
    acc_trade_seven.symbol = 'ZM1May20P133.0'
    acc_trade_seven.underlying_symbol = 'ZM'
    acc_trade_seven.quantity = 1
    acc_trade_seven.trade_price = 1.7
    acc_trade_seven.currency = 'USD'
    acc_trade_seven.commission = 8
    acc_trade_seven.multiplier = 100
    acc_trade_seven.trade_type = trade_type_buy_to_open
    acc_trade_seven.trade_date = datetime.date(2021, 2, 5)

    acc_trade_eight = AccountTrade()
    acc_trade_eight.asset_class = 'OPT'
    acc_trade_eight.symbol = 'ZM1May20P133.0'
    acc_trade_eight.underlying_symbol = 'ZM'
    acc_trade_eight.quantity = 3
    acc_trade_eight.trade_price = 0.7
    acc_trade_eight.currency = 'USD'
    acc_trade_eight.commission = 9
    acc_trade_eight.multiplier = 100
    acc_trade_eight.trade_type = trade_type_sell_to_close
    acc_trade_eight.trade_date = datetime.date(2022, 4, 7)

    #shop short opt
    acc_trade_nine = AccountTrade()
    acc_trade_nine.asset_class = 'OPT'
    acc_trade_nine.symbol = 'SHOP15May20P550.00'
    acc_trade_nine.underlying_symbol = 'SHOP'
    acc_trade_nine.quantity = 7
    acc_trade_nine.trade_price = 2.76
    acc_trade_nine.currency = 'USD'
    acc_trade_nine.commission = 11
    acc_trade_nine.multiplier = 100
    acc_trade_nine.trade_type = trade_type_sell_to_open
    acc_trade_nine.trade_date = datetime.date(2020, 6, 5) 

    acc_trade_ten = AccountTrade()
    acc_trade_ten.asset_class = 'OPT'
    acc_trade_ten.symbol = 'SHOP15May20P550.00'
    acc_trade_ten.underlying_symbol = 'SHOP'
    acc_trade_ten.quantity = 3
    acc_trade_ten.trade_price = 6.5
    acc_trade_ten.currency = 'USD'
    acc_trade_ten.commission = 7
    acc_trade_ten.multiplier = 100
    acc_trade_ten.trade_type = trade_type_sell_to_open
    acc_trade_ten.trade_date = datetime.date(2021, 3, 5)

    acc_trade_eleven = AccountTrade()
    acc_trade_eleven.asset_class = 'OPT'
    acc_trade_eleven.symbol = 'SHOP15May20P550.00'
    acc_trade_eleven.underlying_symbol = 'SHOP'
    acc_trade_eleven.quantity = 10
    acc_trade_eleven.trade_price = 0.3
    acc_trade_eleven.currency = 'USD'
    acc_trade_eleven.commission = 6
    acc_trade_eleven.multiplier = 100
    acc_trade_eleven.trade_type = trade_type_buy_to_close
    acc_trade_eleven.trade_date = datetime.date(2022, 5, 7)



    trades = [acc_trade_one, acc_trade_two, acc_trade_three, acc_trade_four, acc_trade_five, acc_trade_six, acc_trade_seven, acc_trade_eight, acc_trade_nine, acc_trade_ten, acc_trade_eleven, acc_trade_twelve,
              acc_trade_13, acc_trade_14]

    tax_ctx_yr_2020 = TaxContextYear()
    tax_ctx_yr_2020.year = 2020
    usd_currency_2020 = TaxCurrency()
    usd_currency_2020.currency = 'USD'
    usd_currency_2020.fx_rate_to_base = 1.3415
    cad_currency_2020 = TaxCurrency()
    cad_currency_2020.currency = 'CAD'
    cad_currency_2020.fx_rate_to_base = 1
    pln_currency_2020 = TaxCurrency()
    pln_currency_2020.currency = 'PLN'
    pln_currency_2020.fx_rate_to_base = 3444

    tax_ctx_yr_2020.currencies.append(usd_currency_2020)
    tax_ctx_yr_2020.currencies.append(cad_currency_2020)
    tax_ctx_yr_2020.currencies.append(pln_currency_2020)

    tax_ctx_yr_2021 = TaxContextYear()
    tax_ctx_yr_2021.year = 2021
    usd_currency_2021 = TaxCurrency()
    usd_currency_2021.currency = 'USD'
    usd_currency_2021.fx_rate_to_base = 1.2535
    cad_currency_2021 = TaxCurrency()
    cad_currency_2021.currency = 'CAD'
    cad_currency_2021.fx_rate_to_base = 1
    tax_ctx_yr_2021.currencies.append(usd_currency_2021)
    tax_ctx_yr_2021.currencies.append(cad_currency_2021)

    tax_ctx_yr_2022 = TaxContextYear()
    tax_ctx_yr_2022.year = 2022
    usd_currency_2022 = TaxCurrency()
    usd_currency_2022.currency = 'USD'
    usd_currency_2022.fx_rate_to_base = 1.45
    cad_currency_2022 = TaxCurrency()
    cad_currency_2022.currency = 'CAD'
    cad_currency_2022.fx_rate_to_base = 1
    tax_ctx_yr_2022.currencies.append(usd_currency_2022)
    tax_ctx_yr_2022.currencies.append(cad_currency_2022)

    tax_ctx = TaxContext()
    tax_ctx.years.append(tax_ctx_yr_2020)
    tax_ctx.years.append(tax_ctx_yr_2021)
    tax_ctx.years.append(tax_ctx_yr_2022)

    trade_groups = group_trades(trades)
    assert(len(trade_groups) == 4)
    
    assert(trade_groups[0].symbol == 'CODX')
    assert(trade_groups[0].underlying_symbol == 'CODX')
    assert(trade_groups[0].asset_class == 'STK')
    assert(len(trade_groups[0].trades) == 5)
    assert(trade_groups[0].qty_opened == 220)
    assert(trade_groups[0].qty_closed == 220)

    assert(trade_groups[1].symbol == 'ZM1May20P133.0')
    assert(trade_groups[1].underlying_symbol == 'ZM')
    assert(trade_groups[1].asset_class == 'OPT')
    assert(len(trade_groups[1].trades) == 3)
    assert(trade_groups[1].qty_opened == 4)
    assert(trade_groups[1].qty_closed == 3)

    assert(trade_groups[2].symbol == 'SHOP15May20P550.00')
    assert(trade_groups[2].underlying_symbol == 'SHOP')
    assert(trade_groups[2].asset_class == 'OPT')
    assert(len(trade_groups[2].trades) == 3)
    assert(trade_groups[2].qty_opened == 10)
    assert(trade_groups[2].qty_closed == 10)

    assert(trade_groups[3].symbol == 'ZM')
    assert(trade_groups[3].underlying_symbol == 'ZM')
    assert(trade_groups[3].asset_class == 'STK')
    assert(len(trade_groups[3].trades) == 3)
    assert(trade_groups[3].qty_opened == 25)
    assert(trade_groups[3].qty_closed == 25)


    taxes = calculate_taxes(tax_ctx, trade_groups, 2020, 2023)
    '''
        2020
        
        codx stk
        cost_basis = (200 * 17.5 + 6.95) / 200 = 17.53
        sale = 75 * 13.2 - 8.3 = 981.7
        proceeds = 981.7 * 1.3415 = 981.7 usd = 1316.95 cad
        costs = 75 * 17.53 * 1.3415 = 1314.75 usd = 1763.74 cad
        taxes_due = 981.7 - 1314.75 = -333.05 usd = -446.79 cad

        zm short stk
        cost_basis = 400.27
        sale = 0
        proceeds = 0
        taxes_due = 0

        2021 
        sale_one = 2993
        proceeds = 2993 usd
        costs = 10 * 400.27 = 4002.7
        taxes_due = 695 usd - 554.4 usd = 140.6 usd = 176.24 cad

        2022
        sale = (110 * 34 - 7.95) = 3732.05 usd
        proceeds = 3732.05 usd
        cost = 110 * 15.84 = 1742.4 usd
        taxes_due = 3732.05 - 1742.4 = 1989.65 usd = 2884.99 cad
    '''
    assert(len(taxes) == 3) #2020, 2021, 2022
    
    assert(taxes[0].year == 2020)
    assert(round(taxes[0].tax_due, 2) == -333.05)
    assert(round(taxes[0].tax_due_base_currency, 2) == -446.79)

    assert(taxes[1].year == 2021)
    assert(round(taxes[1].tax_due, 2) == 140.6)
    assert(round(taxes[1].tax_due_base_currency, 2) == 176.24)

    assert(taxes[2].year == 2022)
    assert(round(taxes[2].tax_due, 2) == 1989.65)
    assert(round(taxes[2].tax_due_base_currency, 2) == 2884.99)


def calculate_taxes_due_file():
    df = pd.read_csv('/home/ghelie/taxes/2021/taxes_validation.csv')
    df = df.fillna(0)

    ib_taxes = 0
    qt_taxes = 0

    for idx, row in df.iterrows():
        broker = row['Brokerage']

        if row['Brokerage'] == 'ib' or row['Brokerage'] == 'IB':
            ib_taxes += row['t5008_proceeds'] - row['t5008_costs']
            print(row['db_symbol'])
            i = 2
        elif row['Brokerage'] == 'questrade' or row['Brokerage'] == 'QUESTRADE':
            qt_taxes += row['t5008_proceeds'] - row['t5008_costs']

    
    qt_taxes -= 476.29
    qt_taxes -= 855.54
    qt_taxes += 54
    qt_taxes *= 1.2535

    i = 2
        


if __name__ == "__main__":
    #save_account_trades_ibkr()
    #generate_tax_report()
    #match_t5008_with_trade_logs()
    #mark_wash_sales()
    #save_account_trades_questrade()

    calculate_taxes_due_file()

    #save_account_trades_questrade()
    #save_account_trades_ibkr()
    
    '''test()

    tax_ctx_yr_2020 = TaxContextYear()
    tax_ctx_yr_2020.year = 2020
    usd_currency_2020 = TaxCurrency()
    usd_currency_2020.currency = 'USD'
    usd_currency_2020.fx_rate_to_base = 1.3415
    cad_currency_2020 = TaxCurrency()
    cad_currency_2020.currency = 'CAD'
    cad_currency_2020.fx_rate_to_base = 1
    pln_currency_2020 = TaxCurrency()
    pln_currency_2020.currency = 'PLN'
    pln_currency_2020.fx_rate_to_base = 3444

    tax_ctx_yr_2020.currencies.append(usd_currency_2020)
    tax_ctx_yr_2020.currencies.append(cad_currency_2020)
    tax_ctx_yr_2020.currencies.append(pln_currency_2020)

    tax_ctx_yr_2021 = TaxContextYear()
    tax_ctx_yr_2021.year = 2021
    usd_currency_2021 = TaxCurrency()
    usd_currency_2021.currency = 'USD'
    usd_currency_2021.fx_rate_to_base = 1.2535
    cad_currency_2021 = TaxCurrency()
    cad_currency_2021.currency = 'CAD'
    cad_currency_2021.fx_rate_to_base = 1
    tax_ctx_yr_2021.currencies.append(usd_currency_2021)
    tax_ctx_yr_2021.currencies.append(cad_currency_2021)

    tax_ctx = TaxContext()
    tax_ctx.years.append(tax_ctx_yr_2020)
    tax_ctx.years.append(tax_ctx_yr_2021)

    manager = SqlAlchemySessionManager()
    with manager.session_scope(db_url='postgresql://postgres:navo1234@localhost:5432/fin_app_core_db', template_name='default_session') as session:
        #trades = session.query(AccountTrade).order_by(AccountTrade.trade_date.asc()).all()
        trades = session.query(AccountTrade).filter(AccountTrade.underlying_symbol == 'ZM').order_by(AccountTrade.trade_date.asc()).all()
        trade_groups = group_trades(trades)

        taxes = calculate_taxes(tax_ctx, trade_groups, 2020, 2021)
        i = 2'''