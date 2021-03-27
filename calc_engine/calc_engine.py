from db.company_financials import *
from py_common_utils_gh.db_utils.db_utils import SqlAlchemySessionManager


def is_good_dcf_candidate():
    pass

def calculate__average_book_value_of_debt(financials, sort=False):
    if financials.data_type == data_type_quarterly and len(financials) % 4 != 0:
        raise ValueError("Length of financials must be a multiple of 4 when quarterly is used.")
    if sort:
         sorted_financials = sorted(financials, key=lambda x: x.calendar_date, reverse=True)
    
    book_value_of_debt = 0
    if len(sorted_financials) == 4:
        book_value_of_debt = financials[0].debtc + financials[0].debtnc
    elif len(sorted_financials >= 8):
        book_value_of_debt = (financials[0].debtc + financials[4].debtc) / 2 + (financials[0].debtnc + financials[4].debtnc) / 2
    
    return book_value_of_debt

def calculate_weight_of_debt(market_cap, book_value_of_debt): 
    return book_value_of_debt / (market_cap + book_value_of_debt)

def calculate_cost_of_debt(average_book_value_of_debt, int_exp_ttm, average_tax_rate, after_tax=True):
    cost_of_debt = int_exp_ttm / average_book_value_of_debt
    if after_tax:
        cost_of_debt *= (1 - average_tax_rate)
    return cost_of_debt

def calculate_weight_of_equity(market_cap, book_value_of_debt):
    return market_cap / (market_cap + book_value_of_debt)

def calculate_cost_of_equity(risk_free_rate, beta_of_asset, expected_return_of_market): #required rate of return
    #capm is used  
    return risk_free_rate + beta_of_asset * (expected_return_of_market - risk_free_rate)

def calculate_expected_return_of_market():
    return 0.09
    
def calculate_wacc(weight_of_equity, cost_of_equity, weight_of_debt, cost_of_debt):
    #market cap is synonymous to equity
    wacc =  weight_of_equity * cost_of_equity + weight_of_debt * cost_of_debt  

def calculate_consensus_analyst_financial_metric():
    pass

def estimate_future_financial_metric(year_offset, consensus_analyst_prediction, user_prediction, historical_metric_data):
    pass

'''
    PV = present value or intrisinc value today
    FV = future value
    i = discount rate
    n = nb of years
    FV = PV(1 + i)^n
    PV = FV / (1 + i)^n
    i = (FV / PV)^(1/n) - 1
'''
def calculate_present_stock_value(ticker, future_cash_flows, nb_years, discount_rate):
    pass
    #estimate fcf



    #estimate discount factor

    #calculate discounted value of fcf for ten years

    #calculate the discounted perpetuity fcf (beyond ten years)

    #calculate intrinsic value

    #calculate intrisical value per share

def calculate_return_on_equity():
    pass

def calculate_eps():
    pass

if __name__ == "__main__":
    manager = SqlAlchemySessionManager()
    with manager.session_scope(db_url="postgresql://postgres:navo1234@localhost:5432/fin_app_core_db", template_name='default_session') as session:
        aapl_financials = session.query(CompanyQuarterlyFinancialData).filter(CompanyQuarterlyFinancialData.company_id == 13940).order_by(CompanyQuarterlyFinancialData.calendar_date.desc()).all()
        aapl_financials = aapl_financials[:4]
        debt_current = 0
        for fin in aapl_financials:
            debt_current += fin.debtc
        print(debt_current)



