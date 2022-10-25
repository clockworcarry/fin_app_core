# coding: utf-8
from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import *
from sqlalchemy.schema import *

BAR_TYPE_STOCK_TRADE = 1

BAR_TYPE_FIAT_CURRENCY = 1
BAR_TYPE_DIGITAL_CURRENCY = 2

BAR_SIZE_SECOND = 's'
BAR_SIZE_MINUTE = 'min'
BAR_SIZE_HOUR = 'h'
BAR_SIZE_WEEK = 'w'
BAR_SIZE_MONTH = 'mo'
BAR_SIZE_YEAR = 'y'

OCCURENCE_DAILY = 1
OCURRENCE_WEEKLY = 2
OCCURENCE_MONTHLY = 4
OCCURENCE_QUARTERLY = 8
OCCURENCE_YEARLY = 16

METRIC_TYPE_NUMBER = 0
METRIC_TYPE_PERCENTAGE = 1
METRIC_TYPE_CAGR = 2 #a percentage, but applied every year for the duration

METRIC_DURATION_QUARTER = 0
METRIC_DURATION_ANNUAL = 1
METRIC_DURATION_INFINITY = 2
METRIC_DURATION_FIXED = 3

NOTE_TYPE_TEXT = 0
NOTE_TYPE_TEXT_DOC = 1

company_dev_news_relase = 0

trade_type_buy_to_open = 0
trade_type_sell_to_open = 1
trade_type_buy_to_close = 2
trade_type_sell_to_close = 3
trade_type_assigment = 4
trade_type_expiration = 5
trade_type_buy = 6
trade_type_sell = 7

ibkr_brokerage_id = 0
questrade_brokerage_id = 1

from db.base_models import Base, meta

class Account(Base):
    __tablename__ = 'account'

    id = Column(BigInteger, primary_key=True)
    userName = Column(String(30), unique=True)
    password = Column(String(512), unique=False)
    email = Column(String(60), unique=True)
    phone = Column(String(16), unique=True)
    disabled = Column(Boolean, nullable=False, server_default=text("false"))


''' 
class Subscription:
    pass
'''


"""class CountryInfo(Base):
    __tablename__ = 'country_info'

    id = Column(SmallInteger, primary_key=True)
    name = Column(String(60), nullable=False, unique=True)
    name_code = Column(String(10), nullable=False, unique=True)
    currency = Column(String(10), nullable=False)"""


class Sector(Base):
    __tablename__ = 'sector'

    id = Column(Integer, primary_key=True)
    name_code = Column(String(50), nullable=False, unique=True)
    name = Column(String(60), nullable=False, unique=True)


"""class Exchange(Base):
    __tablename__ = 'exchange'

    id = Column(Integer, primary_key=True)
    country_info_id = Column(ForeignKey('country_info.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True)
    name_code = Column(String(10), nullable=False, unique=True)
    name = Column(String(60), unique=True)"""


class Industry(Base):
    __tablename__ = 'industry'

    id = Column(Integer, primary_key=True)
    sector_id = Column(ForeignKey('sector.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True)
    name = Column(String(60), nullable=False, unique=True)
    name_code = Column(String(60), nullable=False, unique=True)


class Company(Base):
    __tablename__ = 'company'

    id = Column(Integer, primary_key=True)
    ticker = Column(String(10), nullable=False, unique=True)
    name = Column(String(200), unique=True)
    delisted = Column(Boolean, nullable=False, index=True, server_default=text("false"))
    creator_id = Column(ForeignKey('account.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    
    #exchanges = relationship("Exchange", secondary=t_company_exchange_relation, backref='companies')
    #sectors = relationship("Sector", secondary=t_company_sector_relation)
    #balance_sheet_data = relationship('BalanceSheetData')
    #income_statement_data = relationship('IncomeStatementData')
    #cash_flow_statement_data = relationship('CashFlowStatementData')


"""class CompanyExchangeRelation(Base):
    __tablename__ = 'company_exchange_relation'

    #id = Column(Integer, primary_key=True)
    company_id = Column(ForeignKey('company.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True, nullable=False)
    exchange_id = Column(ForeignKey('exchange.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True, nullable=False)"""


#many to many relationship between sectors and business segments
class CompanySectorRelation(Base):
    __tablename__ = "company_sector_relation"

    #id = Column(Integer, primary_key=True)
    company_business_segment_id = Column(ForeignKey('company_business_segment.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True, nullable=False)
    sector_id = Column(ForeignKey('sector.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True, nullable=False)

#many to many relationship between industries and business segments
class CompanyIndustryRelation(Base):
    __tablename__ = "company_industry_relation"

    #id = Column(Integer, primary_key=True)
    company_business_segment_id = Column(ForeignKey('company_business_segment.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True, nullable=False)
    industry_id = Column(ForeignKey('industry.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True, nullable=False)


class CompanyBusinessSegment(Base):
    __tablename__ = 'company_business_segment'

    id = Column(Integer, primary_key=True)
    company_id = Column(ForeignKey('company.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True)
    code = Column(String(60), nullable=False)
    display_name = Column(String(120), nullable=False)
    creator_id = Column(ForeignKey('account.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)


#a group of company for comparisons
class CompanyGroup(Base): #can be seen as a sub sector.. used when stocks within a sector are very closely related.. ex: twtr, fb, pins, snap
    __tablename__ = 'company_group'

    id = Column(Integer, primary_key=True)
    name_code = Column(String(50), nullable=False)
    name = Column(String(60), nullable=False)
    description = Column(Text, nullable=True)
    #industry_id = Column(ForeignKey('industry.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=True, index=True)
    creator_id = Column(ForeignKey('account.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)

    __table_args__ = (UniqueConstraint('name_code', 'name', 'creator_id'), )


#all the company groups/business segments in the db
class CompanyInGroup(Base):
    __tablename__ = 'company_in_group'

    company_business_segment_id = Column(ForeignKey('company_business_segment.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True, nullable=False)
    group_id = Column(ForeignKey('company_group.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True, nullable=False)

    #__table_args__ = (UniqueConstraint('company_business_segment_id', 'group_id'), )


#all the company groups that the user has access to (shared with him or he chose to add them to his list of "favorites")
class UserCompanyGroup(Base):
    __tablename__ = 'user_company_group'

    account_id = Column(ForeignKey('account.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True, nullable=False)
    group_id = Column(ForeignKey('company_group.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True, nullable=False)

    #__table_args__ = (UniqueConstraint('account_id', 'group_id'), )


#low write index everything
# a metric description can be shared. Multiple groups/companies can use the same description, only the underlying value/data associated to the
#description will change based on the company
#ex: revenue_growth_2y 
#       -> 20% AAPL
#       -> 15% GOOGL
class MetricDescription(Base):
    __tablename__ = 'metric_description'

    id = Column(BigInteger, primary_key=True)
    code = Column(String(60), nullable=False, index=True)
    display_name = Column(String(120), nullable=False)
    
    metric_data_type = Column(SmallInteger, nullable=False, index=True)
    metric_duration_type = Column(SmallInteger, nullable=False, index=True)
    
    year_recorded = Column(SmallInteger, nullable=False, index=True)
    quarter_recorded = Column(SmallInteger, nullable=False, index=True)
    metric_duration = Column(SmallInteger, nullable=False, index=True)
    look_back = Column(Boolean, nullable=False, index=True)
    
    metric_fixed_year = Column(SmallInteger, nullable=False, index=True)
    metric_fixed_quarter = Column(SmallInteger, nullable=False, index=True)
    
    metric_classification_id = Column(ForeignKey('metric_classification.id', ondelete='SET NULL'), nullable=True)
    creator_id = Column(ForeignKey('account.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=True)

    __table_args__ = (UniqueConstraint('code', 'metric_data_type', 'metric_duration', 'metric_duration_type', 'look_back', 'metric_fixed_year', 'metric_fixed_quarter'), )

#all the metric descriptions that the user can use. Every user will have all the metric descriptions created by the system user by default
#and will also have metric descriptions that they chose to add to their universe
class UserMetricDescription(Base):
    __tablename__ = 'user_metric_description'

    metric_description_id = Column(ForeignKey('metric_description.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True, nullable=False)
    account_id = Column(ForeignKey('account.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True, nullable=False)


#all the metric descriptions in the group
class CompanyGroupMetricDescription(Base):
    __tablename__ = 'company_group_metric_description'

    metric_description_id = Column(ForeignKey('metric_description.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True, nullable=False)
    company_group_id = Column(ForeignKey('company_group.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True, nullable=False)
    
    #__table_args__ = (UniqueConstraint('metric_description_id', 'company_group_id'), )


""" a note associated to a metric description. Binary format so it allows the user to go into
    details when explaining what the metric is in its current context
    certain metrics could mean different things depending on the company
    however, a metric description in a group will have the same meaning for all companies/business segments in the group.

class MetricDescriptionNote(Base):
    __tablename__ = 'metric_description_note'
    
    id = Column(Integer, primary_key=True)
    note_data = Column(LargeBinary, nullable=False)
    note_type = Column(SmallInteger, nullable=False)
    company_metric_relation_id = Column(ForeignKey('company_group_metric_description.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True)"""


#a metric description will have multiple MetricData records associated to it
#because the metric description is unique and is shared. "revenue" is a metric that is used by every company,
#only the underlying value of the metric will be different based on the company
class MetricData(Base):
    __tablename__ = 'metric_data'

    id = Column(BigInteger, primary_key=True)
    metric_description_id = Column(ForeignKey('metric_description.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True)
    company_business_segment_id = Column(ForeignKey('company_business_segment.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True)
    data = Column(Numeric, nullable=False)
    user_id = Column(ForeignKey('account.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True) #if this isn't system, then it is a user-specific override

    __table_args__ = (UniqueConstraint('metric_description_id', 'company_business_segment_id', 'user_id'), )


class ScreenerPreset(Base):
    __tablename__ = 'screener_preset'

    id = Column(BigInteger, primary_key=True)
    name_code = Column(String(30), nullable=False)
    display_name = Column(String(120), nullable=False)
    creator_id = Column(ForeignKey('account.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)


#all the screener presets that a user has access to
class UserScreenerPreset(Base):
    __tablename__ = 'user_screener_preset'

    screener_preset_id = Column(ForeignKey('screener_preset.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True, nullable=False)
    account_id = Column(ForeignKey('account.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True, nullable=False)

    #__table_args__ = (UniqueConstraint('metrics_preset_id', 'account_id'), )


#search params for a screen that were saved by a user or provided by default by the app
class ScreenerPresetData(Base):
    __tablename__ = 'screener_preset_data'

    id = Column(BigInteger, primary_key=True)
    metric_description_id = Column(ForeignKey('metric_description.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False) 
    screener_preset_id = Column(ForeignKey('screener_preset.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    data_numeric = Column(Numeric, nullable=True)
    data_str = Column(String(120), nullable=True)
    
    __table_args__ = (UniqueConstraint('metric_description_id', 'screener_preset_id'), )


class MetricClassification(Base):
    __tablename__ = 'metric_classification'

    id = Column(Integer, primary_key=True)
    category_name = Column(String(120), nullable=False)
    parent_category_id = Column(Integer, nullable=True)
    creator_id = Column(ForeignKey('account.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)


#all the classifications that the user can use.. these are not rights, but what the user wants to use
class UserMetricClassification(Base):
    __tablename__ = 'user_metric_classification'

    metric_classification_id = Column(ForeignKey('metric_classification.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True, nullable=False)
    account_id = Column(ForeignKey('account.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True, nullable=False)

    #__table_args__ = (UniqueConstraint('metric_classification_id', 'account_id'), )

"""class CompanyDevelopment(Base):
    __tablename__ = 'company_development'

    id = Column(BigInteger, primary_key=True)
    company_business_segment_id = Column(ForeignKey('company_business_segment.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True)
    code = Column(String(60), nullable=False) #ex: aapl_dev_2020_01_01
    display_name = Column(String(120), nullable=False) #ex: aapl_dev_2020_01_01
    dev_type = Column(SmallInteger, nullable=False, index=True) #conference, devcon, news release, interview, etc.
    data_type = Column(SmallInteger, nullable=False, index=True) #png, link, text, etc.
    data = Column(LargeBinary)
    date_recorded = Column(Date, nullable=False, index=True)"""

"""class CompanySummary(Base):
    __tablename__ = 'company_summary'

    id = Column(Integer, primary_key=True)
    company_id = Column(ForeignKey('company.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True)
    data = Column(LargeBinary)# rich text (google doc, word, etc.)"""


"""class EquityBarData(Base):
    __tablename__ = 'equity_bar_data'

    id = Column(BigInteger, primary_key=True)
    company_id = Column(ForeignKey('company.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True)
    exchange_id = Column(ForeignKey('exchange.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    bar_type = Column(Integer, nullable=False)
    bar_open = Column(Numeric, nullable=False)
    bar_high = Column(Numeric, nullable=False)
    bar_low = Column(Numeric, nullable=False)
    bar_close = Column(Numeric, nullable=False)
    bar_volume = Column(BigInteger)
    bar_date = Column(DateTime(timezone=True), nullable=False, index=True)
    bar_size = Column(String(12), nullable=False)"""


"""class CurrencyBarData(Base):
    __tablename__ = 'currency_bar_data'

    id = Column(BigInteger, primary_key=True)
    symbol = Column(String(12), nullable=False, index=True)
    bar_type = Column(Integer, nullable=False)
    bar_open = Column(Numeric, nullable=False)
    bar_high = Column(Numeric, nullable=False)
    bar_low = Column(Numeric, nullable=False)
    bar_close = Column(Numeric, nullable=False)
    bar_volume = Column(BigInteger)
    bar_date = Column(DateTime(timezone=True), nullable=False, index=True)
    bar_size = Column(String(12), nullable=False)

    #__table_args__ = (UniqueConstraint('company_id', 'bar_type', 'bar_size', 'bar_date'), )"""

class Log(Base):
    __tablename__ = 'log'

    id = Column(Integer, primary_key=True)
    log_type = Column(String(20), nullable=False, index=True)
    message = Column(String(200))
    data = Column(LargeBinary)


class CronJobRun(Base):
    __tablename__ = 'cron_job_run'

    id = Column(Integer, primary_key=True)
    log_id = Column(ForeignKey('log.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True) 
    success = Column(Boolean, nullable=False)

    log = relationship("Log", uselist=False, backref="cron_job_run")

"""class AccountTrade(Base):
    __tablename__ = 'account_trade'

    id = Column(Integer, primary_key=True)
    currency = Column(String(20), nullable=False, index=True)
    fx_rate_to_base = Column(Numeric, nullable=False)
    asset_class = Column(String(10), nullable=False, index=True)
    underlying_symbol = Column(String(10), nullable=True, index=True)
    symbol = Column(String(60), nullable=False, index=True)
    description = Column(String(200), nullable=True, index=False)
    trade_date = Column(Date, nullable=False, index=True)
    trade_type = Column(SmallInteger, nullable=False, index=True)
    quantity = Column(Integer, nullable=False, index=False)
    strike = Column(Integer, nullable=True, index=False)
    is_call = Column(Boolean, nullable=True, index=False)
    expiry = Column(Date, nullable=True, index=True)
    multiplier = Column(Integer, nullable=True, index=False)
    trade_price = Column(Numeric, nullable=False, index=False)
    commission = Column(Numeric, nullable=False, index=False)
    commission_currency = Column(String(20), nullable=False, index=True)
    cost_basis = Column(Numeric, nullable=False, index=False)
    proceeds = Column(Numeric, nullable=False, index=False)
    update_stamp = Column(DateTime(timezone=True), nullable=False, server_default=FetchedValue())
    brokerage_id = Column(SmallInteger, nullable=False, index=True)"""