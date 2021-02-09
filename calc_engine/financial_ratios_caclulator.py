import pandas as pd

from db.company_financials import BalanceSheetData, IncomeStatementData, CashFlowStatementData, CompanyFundamentalRatios

def compute_financial_ratios(financial_data):
    """
        Computes the financial ratios for a list of tickers. It is recomended that the list of tickers does not exceed 1000.
        This function assumes that the financial statements are sorted in descending order.

    Args:
        financial_data (list(tuple(ticker, list(BalanceSheetData), list(IncomeStatementData), list(CashjFlowStatementData)))): list of tuples of data needed for ratios computation

    @return pd.DataFrame with computed ratios
    """

    
    
