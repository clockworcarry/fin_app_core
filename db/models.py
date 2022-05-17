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

class CompanyExchangeRelation(Base):
    __tablename__ = 'company_exchange_relation'

    company_id = Column(ForeignKey('company.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True, nullable=False)
    exchange_id = Column(ForeignKey('exchange.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True, nullable=False)
    update_stamp = Column(DateTime(timezone=True), nullable=False, server_default=FetchedValue())

class CompanySectorRelation(Base):
    __tablename__ = "company_sector_relation"

    group_id = Column(ForeignKey('company_group.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True, nullable=False)
    sector_id = Column(ForeignKey('sector.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True, nullable=False)
    update_stamp = Column(DateTime(timezone=True), nullable=False, server_default=FetchedValue())

class Company(Base):
    __tablename__ = 'company'

    id = Column(Integer, primary_key=True)
    ticker = Column(String(10), nullable=False, unique=True)
    name = Column(String(200), unique=True)
    locked = Column(Boolean, nullable=False, server_default=text("false"))
    delisted = Column(Boolean, nullable=False, index=True, server_default=text("false"))
    update_stamp = Column(DateTime(timezone=True), nullable=False, server_default=FetchedValue())
    
    #exchanges = relationship("Exchange", secondary=t_company_exchange_relation, backref='companies')
    #sectors = relationship("Sector", secondary=t_company_sector_relation)
    #balance_sheet_data = relationship('BalanceSheetData')
    #income_statement_data = relationship('IncomeStatementData')
    #cash_flow_statement_data = relationship('CashFlowStatementData')

class CompanyGroupRelation(Base):
    __tablename__ = 'company_group_relation'

    company_business_or_product_id = Column(ForeignKey('company_business_or_product.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True, nullable=False)
    group_id = Column(ForeignKey('company_group.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True, nullable=False)
    update_stamp = Column(DateTime(timezone=True),  nullable=False, server_default=FetchedValue())

class CompanyGroup(Base): #can be seen as a sub sector.. used when stocks within a sector are very closely related.. ex: twtr, fb, pins, snap
    __tablename__ = 'company_group'

    id = Column(Integer, primary_key=True)
    name_code = Column(String(50), nullable=False, unique=True)
    name = Column(String(60), nullable=False, unique=True)
    description = Column(Text, nullable=True, unique=False)
    industry_id = Column(ForeignKey('industry.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=True, index=True)
    update_stamp = Column(DateTime(timezone=True), nullable=False, server_default=FetchedValue())


class CountryInfo(Base):
    __tablename__ = 'country_info'

    id = Column(SmallInteger, primary_key=True)
    name = Column(String(60), nullable=False, unique=True)
    name_code = Column(String(10), nullable=False, unique=True)
    currency = Column(String(10), nullable=False)
    update_stamp = Column(DateTime(timezone=True), nullable=False, server_default=FetchedValue())


class Sector(Base):
    __tablename__ = 'sector'

    id = Column(SmallInteger, primary_key=True)
    name_code = Column(String(50), nullable=False, unique=True)
    name = Column(String(60), nullable=False, unique=True)
    locked = Column(Boolean, nullable=False, server_default=text("false"))
    update_stamp = Column(DateTime(timezone=True), nullable=False, server_default=FetchedValue())


class Exchange(Base):
    __tablename__ = 'exchange'

    id = Column(SmallInteger, primary_key=True)
    country_info_id = Column(ForeignKey('country_info.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True)
    name_code = Column(String(10), nullable=False, unique=True)
    name = Column(String(60), unique=True)
    update_stamp = Column(DateTime(timezone=True), nullable=False, server_default=FetchedValue())


class Industry(Base):
    __tablename__ = 'industry'

    id = Column(SmallInteger, primary_key=True)
    sector_id = Column(ForeignKey('sector.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True)
    name = Column(String(60), nullable=False, unique=True)
    name_code = Column(String(60), nullable=False, unique=True)
    locked = Column(Boolean, nullable=False, server_default=text("false"))
    update_stamp = Column(DateTime(timezone=True), nullable=False, server_default=FetchedValue())


class EquityBarData(Base):
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
    bar_size = Column(String(12), nullable=False)
    locked = Column(Boolean, nullable=False, server_default=text("false"))

class CurrencyBarData(Base):
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
    locked = Column(Boolean, nullable=False, server_default=text("false"))

    #__table_args__ = (UniqueConstraint('company_id', 'bar_type', 'bar_size', 'bar_date'), )

class CompanyMetric(Base): #Very low write, every column can be indexed
    __tablename__ = 'company_metric'

    id = Column(Integer, primary_key=True)
    company_metric_relation_id = Column(ForeignKey('company_metric_relation.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True)
    company_business_or_product_id = Column(ForeignKey('company_business_or_product.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True) 
    data = Column(Numeric, nullable=False)
    date_recorded = Column(Date, nullable=False, index=True)

#low write index everything
class CompanyMetricDescription(Base):
    __tablename__ = 'company_metric_description'

    id = Column(Integer, primary_key=True)
    code = Column(String(60), nullable=False, index=True)
    display_name = Column(String(120), nullable=False)
    metric_data_type = Column(SmallInteger, nullable=False, index=True)
    metric_duration = Column(SmallInteger, nullable=False, index=True)
    metric_duration_type = Column(SmallInteger, nullable=False, index=True)
    look_back = Column(Boolean, nullable=False, index=True)
    update_stamp = Column(DateTime(timezone=True), nullable=False, server_default=FetchedValue(), index=True)

    __table_args__ = (UniqueConstraint('code', 'metric_data_type', 'metric_duration', 'metric_duration_type', 'look_back'), )

class CompanyMetricDescriptionNote(Base):
    __tablename__ = 'company_metric_description_note'
    
    id = Column(Integer, primary_key=True)
    note_data = Column(LargeBinary, nullable=False)
    note_type = Column(SmallInteger, nullable=False)
    company_metric_relation_id = Column(ForeignKey('company_metric_relation.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True)
    update_stamp = Column(DateTime(timezone=True), nullable=False, server_default=FetchedValue(), index=True)

class CompanyMetricRelation(Base):
    __tablename__ = 'company_metric_relation'

    id = Column(Integer, primary_key=True)
    company_metric_description_id = Column(ForeignKey('company_metric_description.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    company_group_id = Column(ForeignKey('company_group.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=True)
    update_stamp = Column(DateTime(timezone=True), nullable=False, server_default=FetchedValue(), index=True)
    
    __table_args__ = (UniqueConstraint('company_metric_description_id', 'company_group_id'), )

class CompanyBusinessOrProduct(Base):
    __tablename__ = 'company_business_or_product'

    id = Column(Integer, primary_key=True)
    company_id = Column(ForeignKey('company.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True)
    code = Column(String(60), nullable=False)
    display_name = Column(String(120), nullable=False)

class CompanyDevelopment(Base):
    __tablename__ = 'company_development'

    id = Column(BigInteger, primary_key=True)
    company_business_or_product = Column(ForeignKey('company_business_or_product.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True)
    code = Column(String(60), nullable=False) #ex: aapl_dev_2020_01_01
    display_name = Column(String(120), nullable=False) #ex: aapl_dev_2020_01_01
    dev_type = Column(SmallInteger, nullable=False, index=True) #conference, devcon, news release, interview, etc.
    data_type = Column(SmallInteger, nullable=False, index=True) #png, link, text, etc.
    data = Column(LargeBinary)
    date_recorded = Column(Date, nullable=False, index=True)

class CompanySummary(Base):
    __tablename__ = 'company_summary'

    id = Column(Integer, primary_key=True)
    company_id = Column(ForeignKey('company.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True)
    data = Column(LargeBinary)# rich text (google doc, word, etc.)
    update_stamp = Column(DateTime(timezone=True), nullable=False, server_default=FetchedValue(), index=True)

class Log(Base):
    __tablename__ = 'log'

    id = Column(Integer, primary_key=True)
    log_type = Column(String(20), nullable=False, index=True)
    message = Column(String(200))
    data = Column(LargeBinary)
    update_stamp = Column(DateTime(timezone=True), nullable=False, server_default=FetchedValue())


class CronJobRun(Base):
    __tablename__ = 'cron_job_run'

    id = Column(Integer, primary_key=True)
    log_id = Column(ForeignKey('log.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True) 
    success = Column(Boolean, nullable=False)

    log = relationship("Log", uselist=False, backref="cron_job_run")

class AccountTrade(Base):
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
    brokerage_id = Column(SmallInteger, nullable=False, index=True)



class ImportCompaniesReport:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.info = []
        self.tickers_with_name_changes = []
        self.company_names_with_ticker_changes = []

def create_database(args):
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument('--db_url', help="The database url the command targets.")
        parser.add_argument('--log_file_path', help="Location of the info logs.")
        args, unknown = parser.parse_known_args()

        handler = logging.FileHandler(args.log_file_path)
        handler.setLevel(logging.INFO)

        logger = logging.getLogger('sqlalchemy')
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

        engine = create_engine(args.db_url, echo=True)
        Base.metadata.create_all(engine)
    except Exception as gen_ex:
        print(str(gen_ex))