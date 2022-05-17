from fastapi import APIRouter, status, HTTPException
from typing import Optional, List
from pydantic import BaseModel, ValidationError, validator

from py_common_utils_gh.os_common_utils import setup_logger, default_log_formatter
from py_common_utils_gh.db_utils.db_utils import SqlAlchemySessionManager
from db.models import *
from db.company_financials import *
import numpy as np
from psycopg2 import *
from sqlalchemy import create_engine, select, insert, exists
from sqlalchemy.orm import sessionmaker

from calc_engine.calc_engine import *

import datetime, base64, sys, math

import simplejson as json

import api.config as api_config

router = APIRouter(
    prefix="/company/financials",
    tags=["companyFinancials"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)

class CompanyFinancialsApiModel(BaseModel):
    id: int
    calendar_date: datetime.date
    date_filed: datetime.date
    data_type: int

    assets: int = None #assets 
    cash_and_equivalents: int = None #cashneq
    investments: int = None #investments
    investments_current: int = None #investmentsc
    investments_non_current: int = None #investmentsnc
    deferred_revenue: int = None # deferredrev
    deposits: int = None #deposits
    property_and_plant_equip_net: int = None #ppenet
    inventory: int = None #inventory
    tax_assets: int = None #taxassets
    receivables: int = None #receivables
    payables: int = None #payables
    intangibles: int = None #intangibles
    liabilities: int = None #liabilities
    equity: int = None #equity
    accumulated_retained_earnings: int = None #retearn
    accumulated_other_comprehensive_income: int = None #accoci
    assets_current: int = None #assetsc
    assets_non_current: int = None #assetsnc
    liabilities_current: int = None #liabilitiesc
    liabilities_non_current: int = None #liabilitiesnc
    tax_liabilities: int = None #taxliabilities
    debt: int = None #debt
    debt_current: int = None #debtc
    debt_non_current: int = None #debtnc
    revenue: int = None #revenue
    cost_of_revenue: int = None #cor
    operating_expense: int = None #opex
    sgna: int = None #sgna
    rnd: int = None #rnd
    interest_expense: int = None #intexp
    tax_expense: int = None #taxexp
    net_income_loss_discontinued_operations: int = None #netincdis
    consolidated_income: int = None #consolinc
    net_income_non_controlling_interests: int = None #netincnci
    net_income: int = None #netinc
    preferred_dividends_impact: int = None #prefdivis
    net_income_common_stock: int = None #netinccmn
    capex: int = None #capex
    net_cash_flow_business_acquisitions_and_disposal: int = None #ncfbus
    net_cash_flow_from_investing: int = None #ncfi
    net_cash_flow_investment_acquisitions_and_disposal: int = None #ncfinv
    net_cash_flow_from_financing: int = None #ncff
    repayment_of_debt_securities: int = None #ncfdebt
    purchase_of_equity_shares: int = None #ncfcommon
    payment_of_dividends_and_other_cash_distributions: int = None #ncfdiv
    net_cash_flow_from_operations: int = None #ncfo
    effect_exchange_rates_on_cash: int = None #ncfx
    net_cash_flow: int = None #ncf
    share_based_compensation: int = None #sbcomp
    depreciation_amortization_accretion: int = None #depamor

    basic_shares_basic_outstanding: int = None #sharesbas
    weighted_average_shares: int = None #shareswa
    weighted_average_shares_diluted: int = None #shareswadil

    effective_tax_rate: float = None #effective_tax_rate

    fx_usd: float = None #fx_usd

    locked: bool = None #locked

class CompanyFinancialsApiModelOut(BaseModel):
    id: int
    calendar_date: datetime.date
    data_type: int

class CompanyFinancialStatsOut(BaseModel):
    id: int
    pe_ttm: float
    pb_ttm: float
    ps_ttm: float
    pfcf_ttm: float
    monthly_vol_as_percentage_shares_outstanding: float
    price_to_equity: float
    eps: float
    roe: float
    gross_margin: float
    net_profit_margin: float
    current_ratio: float
    total_debt_to_equity: float
    ev: float
    ev_to_ebidta: float
    pfe: float #price to forward earnings
    eps_change_ttm: float
    eps_change_mrq: float #compared to same quarter previous year
    market_cap: float
    shares_outstanding: int
    stock_price: float
    intrinsic_value: float
    #custom metrics + analyst ratings

class FcfGrowth(BaseModel):
    index: int
    nb_years: int
    rev_cagr: float
    net_income_margin: float
    fcf_to_net_income_ratio: float
    is_terminal: bool

class RevenueGrowthDefault(BaseModel):
    index: int
    nb_years: int
    cagr: float
    is_terminal: bool

class DcfParams(BaseModel):
    avg_book_value_of_debt: float = None
    discount_rate: float = None #if not specified, wacc will be used = 
    cost_of_debt: float = None
    risk_free_rate: float = None
    beta_asset: float = None
    expected_market_return: float = None
    int_exp: float = None
    avg_tax_rate: float = None
    
    fcf_growth_periods: List[FcfGrowth]
    perpetual_growth_rate: float


class CompanyFinancialStatsIn(BaseModel):
    stock_price: float
    shares_bas: int

    calculate_intrinsic_value: bool
    dcf_params: DcfParams = None

class FcfGrowthOut(BaseModel):
    index: int
    nb_years: int
    avg_historical_rev_cagr: float
    avg_historical_rev_cagr: float
    low_historical_rev_cagr: float
    high_historical_rev_cagr: float
    avg_historical_net_income_margin: float
    low_historical_net_income_margin: float
    high_historical_net_income_margin: float
    avg_historical_fcf_to_net_income_ratio: float
    low_historical_fcf_to_net_income_ratio: float
    high_historical_fcf_to_net_income_ratio: float

class DcfParamsDefaultOut(BaseModel):
    avg_book_value_of_debt: float = None
    discount_rate: float = None #if not specified, wacc will be used = 
    cost_of_debt: float = None
    risk_free_rate: float = None
    beta_asset: float = None
    expected_market_return: float = None
    int_exp: float = None
    avg_tax_rate: float = None
    
    fcf_growth_periods: List[FcfGrowthOut]
    perpetual_growth_rate: float

class CompanyFinancialStatsDefaultOut(BaseModel):
    stock_price: float
    shares_bas: int

    dcf_params: DcfParamsDefaultOut = None

    dcf_score: int

    has_financials: bool


@router.post("/{company_id}", response_model=CompanyFinancialsApiModelOut)
def create_financials(company_id, body: CompanyFinancialsApiModel):
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            db_financials = CompanyFinancialData()

            db_financials.company_id = company_id
            db_financials.data_type = body.data_type
            db_financials.calendar_date = body.calendar_date
            db_financials.date_filed = body.date_filed

            db_financials.assets = body.assets
            db_financials.cashneq = body.cash_and_equivalents
            db_financials.investments = body.investments
            db_financials.investmentsc = body.investments_current
            db_financials.investmentsnc = body.investments_non_current
            db_financials.deferredrev = body.deferred_revenue
            db_financials.deposits = body.deposits
            db_financials.ppnenet = body.property_and_plant_equip_net
            db_financials.inventory = body.inventory
            db_financials.taxassets = body.tax_assets
            db_financials.receivables = body.receivables
            db_financials.payables = body.payables
            db_financials.intangibles = body.intangibles
            db_financials.liabilities = body.liabilities
            db_financials.equity = body.equity
            db_financials.retearn = body.accumulated_retained_earnings
            db_financials.accoci = body.accumulated_other_comprehensive_income
            db_financials.assetsc = body.assets_current
            db_financials.assetsnc = body.assets_non_current
            db_financials.liabilitiesc = body.liabilities_current
            db_financials.liabilitiesnc = body.liabilities_non_current
            db_financials.taxliabilities = body.tax_liabilities
            db_financials.debt = body.debt
            db_financials.debtc = body.debt_current
            db_financials.debtnc = body.debt_non_current
            db_financials.revenue = body.revenue
            db_financials.cor = body.cost_of_revenue
            db_financials.opex = body.operating_expense
            db_financials.sgna = body.sgna
            db_financials.rnd = body.rnd
            db_financials.intexp = body.interest_expense
            db_financials.taxexp = body.consolidated_income
            db_financials.netincnci = body.net_income_non_controlling_interests
            db_financials.netinc = body.net_income
            db_financials.prefdivis = body.preferred_dividends_impact
            db_financials.netinccmn = body.net_income_common_stock
            db_financials.capex = body.capex
            db_financials.ncfbus = body.net_cash_flow_business_acquisitions_and_disposal
            db_financials.ncfi = body.net_cash_flow_from_investing
            db_financials.ncfinv = body.net_cash_flow_investment_acquisitions_and_disposal
            db_financials.ncff = body.net_cash_flow_from_financing
            db_financials.ncfdebt = body.repayment_of_debt_securities
            db_financials.ncfcommon = body.purchase_of_equity_shares
            db_financials.ncfdiv = body.payment_of_dividends_and_other_cash_distributions
            db_financials.ncfo = body.net_cash_flow_from_operations
            db_financials.ncfx = body.effect_exchange_rates_on_cash
            db_financials.ncf = body.net_cash_flow
            db_financials.sbcomp = body.share_based_compensation
            db_financials.depamor = body.depreciation_amortization_accretion

            db_financials.sharesbas = body.basic_shares_basic_outstanding
            db_financials.shareswa = body.weighted_average_shares
            db_financials.shareswadil = body.weighted_average_shares_diluted

            db_financials.effective_tax_rate = body.effective_tax_rate

            db_financials.fx_usd = body.fx_usd

            db_financials.locked = body.locked

            session.add(db_financials)
            session.flush()
            ret = CompanyFinancialsApiModelOut(id=db_financials.id, calendar_date=db_financials.calendar_date, data_type=db_financials.data_type)
            return ret

            
    except ValidationError as val_err:
        raise HTTPException(status_code=500, detail=str(val_err))
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))

@router.get("/{company_id}/{calendar_date}/{data_type}", response_model=CompanyFinancialsApiModel)
def get_financials(company_id, calendar_date, data_type):
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            db_financials = session.query(CompanyFinancialData).filter(and_(CompanyFinancialData.company_id == company_id, CompanyFinancialData.calendar_date == calendar_date,
                                                                            CompanyFinancialData.data_type == data_type)).first()
            if db_financials is None:
                raise HTTPException(status_code=500, detail="No financial report with date: " + str(calendar_date) + " or company_id " + str(company_id) + " exists.")
            
            ret = CompanyFinancialsApiModel(id=db_financials.id, calendar_date=db_financials.calendar_date, date_filed=db_financials.date_filed, data_type=db_financials.data_type, assets=db_financials.assets, cash_and_equivalents=db_financials.cashneq, \
                                            investments=db_financials.investments, investments_current=db_financials.investmentsc, investments_non_current=db_financials.investmentsnc, \
                                            deferred_revenue=db_financials.deferredrev, deposits=db_financials.deposits, property_and_plant_equip_net=db_financials.ppnenet, inventory=db_financials.inventory, \
                                            tax_assets=db_financials.taxassets, receivables=db_financials.receivables, payables=db_financials.payables, intangibles=db_financials.intangibles, \
                                            liabilities=db_financials.liabilities, equity=db_financials.equity, accumulated_retained_earnings=db_financials.retearn, \
                                            accumulated_other_comprehensive_income=db_financials.accoci, assets_current=db_financials.assetsc, assets_non_current=db_financials.assetsnc, \
                                            liabilities_current=db_financials.liabilitiesc, liabilities_non_current=db_financials.liabilitiesnc, tax_liabilities=db_financials.taxliabilities, \
                                            debt=db_financials.debt, debt_current=db_financials.debtc, debt_non_current=db_financials.debtnc, revenue=db_financials.revenue, cost_of_revenue=db_financials.cor, \
                                            operating_expense=db_financials.opex, sgna=db_financials.sgna, rnd=db_financials.rnd, interest_expense=db_financials.intexp, tax_expense=db_financials.taxexp, \
                                            net_income_loss_discontinued_operations=db_financials.netincdis, consolidated_income=db_financials.consolinc, net_income_non_controlling_interests=db_financials.netincnci, \
                                            net_income=db_financials.netinc, preferred_dividends_impact=db_financials.prefdivis, net_income_common_stock=db_financials.netinccmn, capex=db_financials.capex, \
                                            net_cash_flow_business_acquisitions_and_disposal=db_financials.ncfbus, net_cash_flow_from_investing=db_financials.ncfi, \
                                            net_cash_flow_investment_acquisitions_and_disposal=db_financials.ncfinv, net_cash_flow_from_financing=db_financials.ncff, repayment_of_debt_securities=db_financials.ncfdebt, \
                                            purchase_of_equity_shares=db_financials.ncfcommon, payment_of_dividends_and_other_cash_distributions=db_financials.ncfdiv, net_cash_flow_from_operations=db_financials.ncfo, \
                                            effect_exchange_rates_on_cash=db_financials.ncfx, net_cash_flow=db_financials.ncf, share_based_compensation=db_financials.sbcomp, \
                                            depreciation_amortization_accretion=db_financials.depamor, basic_shares_basic_outstanding=db_financials.sharesbas, weighted_average_shares=db_financials.shareswa, \
                                            weighted_average_shares_diluted=db_financials.shareswadil, effective_tax_rate=db_financials.effective_tax_rate, fx_usd=db_financials.fx_usd, locked=db_financials.locked
                                        )
            return ret
            
    except ValidationError as val_err:
        raise HTTPException(status_code=500, detail=str(val_err))
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))

@router.get("/{company_id}", response_model=List[CompanyFinancialsApiModel])
def get_financials(company_id):
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            db_financials = session.query(CompanyFinancialData).filter(CompanyFinancialData.company_id == company_id).order_by(CompanyFinancialData.calendar_date.desc()).all()
            if db_financials is None:
                raise HTTPException(status_code=500, detail="No financial report with company_id: " + str(company_id) + " exists.")

            ret = []
            for fin in db_financials:
                ret_elem = CompanyFinancialsApiModel(id=fin.id, calendar_date=fin.calendar_date, assets=fin.assets, cash_and_equivalents=fin.cashneq, \
                                            investments=fin.investments, investments_current=fin.investmentsc, investments_non_current=fin.investmentsnc, \
                                            deferred_revenue=fin.deferredrev, deposits=fin.deposits, property_and_plant_equip_net=fin.ppnenet, inventory=fin.inventory, \
                                            tax_assets=fin.taxassets, receivables=fin.receivables, payables=fin.payables, intangibles=fin.intangibles, \
                                            liabilities=fin.liabilities, equity=fin.equity, accumulated_retained_earnings=fin.retearn, \
                                            accumulated_other_comprehensive_income=fin.accoci, assets_current=fin.assetsc, assets_non_current=fin.assetsnc, \
                                            liabilities_current=fin.liabilitiesc, liabilities_non_current=fin.liabilitiesnc, tax_liabilities=fin.taxliabilities, \
                                            debt=fin.debt, db_current=fin.debtc, debt_non_current=fin.debtnc, revenue=fin.revenue, cost_of_revenue=fin.cor, \
                                            operating_expense=fin.opex, sgna=fin.sgna, rnd=fin.rnd, interest_expense=fin.intexp, tax_expense=fin.taxexp, \
                                            net_income_loss_discontinued_operations=fin.netincdis, consolidated_income=fin.consolinc, net_income_non_controlling_interests=fin.netincnci, \
                                            net_income=fin.netinc, preferred_dividends_impact=fin.prefdivis, net_income_common_stock=fin.netinccmn, capex=fin.capex, \
                                            net_cash_flow_business_acquisitions_and_disposal=fin.ncfbus, net_cash_flow_from_investing=fin.ncfi, \
                                            net_cash_flow_investment_acquisitions_and_disposal=fin.ncfinv, net_cash_flow_from_financing=fin.ncff, repayment_of_debt_securities=fin.ncfdebt, \
                                            purchase_of_equity_shares=fin.ncfcommon, payment_of_dividends_and_other_cash_distributions=fin.ncfdiv, net_cash_flow_from_operations=fin.ncfo, \
                                            effect_exchange_rates_on_cash=fin.ncfx, net_cash_flow=fin.ncf, share_based_compensation=fin.sbcomp, \
                                            depreciation_amortization_accretion=fin.depamor, basic_shares_basic_outstanding=fin.sharesbas, weighted_average_shares=fin.shareswa, \
                                            weighted_average_shares_diluted=fin.shareswadil, effective_tax_rate=fin.effective_tax_rate, fx_usd=fin.fx_usd, locked=fin.locked
                                        )
                ret.append(ret_elem)

            return ret
            
    except ValidationError as val_err:
        raise HTTPException(status_code=500, detail=str(val_err))
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))

@router.get("/statistics/default/{company_id}", response_model=CompanyFinancialStatsDefaultOut)
def get_default_company_stats_params(company_id):
    try:
        manager = SqlAlchemySessionManager()

        ret = CompanyFinancialStatsDefaultOut(has_financials=False)

        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            db_financials_annual = session.query(CompanyFinancialData).filter(CompanyFinancialData.company_id == company_id, CompanyFinancialData.data_type==DATA_TYPE_ANNUAL) \
                                          .order_by(CompanyFinancialData.calendar_date.desc()).all()
            if db_financials_annual is None or len(db_financials) < 3:
                ret.dcf_score = 0
                return ret
            db_financials_quarterly = session.query(CompanyFinancialData).filter(CompanyFinancialData.company_id == company_id, CompanyFinancialData.data_type==DATA_TYPE_QUARTERLY) \
                                             .order_by(CompanyFinancialData.calendar_date.desc()).all()
            if db_financials_quarterly is None or len(db_financials_quarterly) == 0:
                ret.dcf_score = 0
                return ret
            else:
                ret.has_financials = True
                last_daily_bar = session.query(EquityBarData).filter(EquityBarData.company_id == company_id).order_by(EquityBarData.bar_date.desc()).first()
                if last_daily_bar is not None:
                    ret.stock_price = last_daily_bar.bar_close
                
                ret.shares_bas = db_financials_quarterly[0].shares_bas
                
                ret.dcf_params.avg_book_value_of_debt = calculate_average_book_value_of_debt(db_financials_annual, False, DATA_TYPE_ANNUAL)               
                ret.dcf_params.risk_free_rate = 0.02
                ret.dcf_params.int_exp = db_financials_annual[0].intexp
                ret.dcf_params.avg_tax_rate = 0.21
                ret.dcf_params.expected_market_return = 0.09
                ret.dcf_params.perpetual_growth_rate = 0.025

                ret.dcf_params.fcf_growth_periods = []
                growth_period = FcfGrowthOut()
                growth_period.nb_years = 5
                growth_period.index = 0
                nb_years_back = 5
                if len(db_financials_annual) < 5:
                    nb_years_back = len(db_financials_annual)
                
                historical_financials = db_financials_annual[:nb_years_back]

                rev_cagr_history = []
                #for fin in historical_financials:



                    
                    

            
            
    except ValidationError as val_err:
        raise HTTPException(status_code=500, detail=str(val_err))
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))

@router.post("/statistics/{company_id}", response_model=CompanyFinancialStatsOut)
def get_company_stats(company_id, body: CompanyFinancialStatsIn):
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            db_quarterly_financials = session.query(CompanyFinancialData).filter(CompanyFinancialData.company_id == company_id, CompanyFinancialData.data_type==DATA_TYPE_QUARTERLY) \
                                                        .order_by(CompanyFinancialData.calendar_date.desc()).all()
            if db_quarterly_financials is None:
                raise HTTPException(status_code=500, detail="No quarterly financial report with company_id: " + str(company_id) + " exists.")

            if len(db_quarterly_financials) < 4:
                raise HTTPException(status_code=500, detail="A minimum of four quarterly financial reports must exist.")

            db_annual_financials = session.query(CompanyFinancialData).filter(CompanyFinancialData.company_id == company_id, CompanyFinancialData.data_type==DATA_TYPE_ANNUAL) \
                                                        .order_by(CompanyFinancialData.calendar_date.desc()).all()

            if db_annual_financials is None or len(db_annual_financials) < 1:
                raise HTTPException(status_code=500, detail="A minimum of one annual financial report must exist.")
            
            intrinsic_value = None
            stock_price = 0
            pe_ttm = 0
            pb_ttm = 0
            eps_ttm = 0
            shares_bas = 0

            if body.stock_price is None:
                raise HTTPException(status_code=500, detail="A stock price must be provided.")

            if body.shares_bas is None:
                raise HTTPException(status_code=500, detail="Number of shares outstanding must be provided.")

            market_cap = body.stock_price * body.shares_bas

            financials_ttm = db_quarterly_financials[:4]

            for fin in financials_ttm:
                fin_eps = (fin.netinc - fin.prefdivis) / (fin.sharesbas)
                eps_ttm += fin_eps

            bvps = financials_ttm[0].equity / financials_ttm[0].sharesbas
            pb_ttm = body.stock_price / bvps

            pe_ttm = float(body.stock_price) / eps_ttm

            if body.calculate_intrinsic_value:
                if body.dcf_params is None:
                    raise HTTPException(status_code=500, detail="Mandatory dcf_params required.")
                
                discount_rate = 0
                if body.dcf_params.discount_rate is not None:
                    discount_rate = body.dcf_params.discount_rate
                else:
                    cost_of_equity = calculate_cost_of_equity(body.dcf_params.risk_free_rate, body.dcf_params.beta_asset, body.dcf_params.expected_market_return)
                    cost_of_debt = calculate_cost_of_debt(body.dcf_params.avg_book_value_of_debt, body.dcf_params.int_exp, body.dcf_params.avg_tax_rate)
                    weight_of_equity = calculate_weight_of_equity(market_cap, body.dcf_params.avg_book_value_of_debt)
                    weight_of_debt = calculate_weight_of_debt(market_cap, body.dcf_params.avg_book_value_of_debt)
                    discount_rate = weight_of_equity * cost_of_equity + weight_of_debt * cost_of_debt #wacc

                curr_revenue = db_annual_financials[0].revenue
                estimated_free_cash_flows = [] #starts at current year
                for reg in body.dcf_params.fcf_growth_periods:
                    for i in range(reg.nb_years):
                        new_revenue = curr_revenue + (curr_revenue * reg.rev_cagr)
                        new_net_income = new_revenue * reg.net_income_margin
                        new_free_cash_flow = new_net_income * reg.fcf_to_net_income_ratio
                        estimated_free_cash_flows.append(new_free_cash_flow)
                        curr_revenue =  new_revenue

                present_value_of_cash_flows = []
                for idx, fcf in enumerate(estimated_free_cash_flows):
                    discount_factor = pow((1 + discount_rate), idx + 1)
                    present_value_of_cash_flows.append(fcf / discount_factor)
                    if idx == len(estimated_free_cash_flows) - 1: #add terminal value
                        terminal_value = calculate_terminal_value(body.dcf_params.perpetual_growth_rate, fcf, discount_rate)
                        terminal_value_present = terminal_value / discount_factor
                        present_value_of_cash_flows.append(terminal_value_present)

                present_value_of_future_cash_flows = 0
                for pvcf in present_value_of_cash_flows:
                    present_value_of_future_cash_flows += pvcf

                intrinsic_value = present_value_of_future_cash_flows / body.shares_bas
                

            ret = CompanyFinancialStatsOut(id=company_id, pe_ttm = pe_ttm, pb_ttm=pb_ttm, ps_ttm=0, pfcf_ttm=0, monthly_vol_as_percentage_shares_outstanding=0, price_to_equity=0, eps=0, roe=0, gross_margin=0, net_profit_margin=0, \
                                            current_ratio=0, total_debt_to_equity=0, ev=0, ev_to_ebidta=0, pfe=0, eps_change_ttm=0, eps_change_mrq=0, market_cap=0, shares_outstanding=0, stock_price=body.stock_price, \
                                            intrinsic_value=intrinsic_value
            )
        
            return ret
            
    except ValidationError as val_err:
        raise HTTPException(status_code=500, detail=str(val_err))
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))
