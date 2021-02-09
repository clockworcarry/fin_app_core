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

from db.base_models import Base, meta

t_company_exchange_relation = Table(
    'company_exchange_relation', meta,
    Column('company_id', ForeignKey('company.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True, nullable=False),
    Column('exchange_id', ForeignKey('exchange.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True, nullable=False),
    Column('update_stamp', DateTime(timezone=True), nullable=False, server_default=FetchedValue())
)

t_company_sector_relation = Table(
    'company_sector_relation', meta,
    Column('company_id', ForeignKey('company.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True, nullable=False),
    Column('sector_id', ForeignKey('sector.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True, nullable=False),
    Column('update_stamp', DateTime(timezone=True), nullable=False, server_default=FetchedValue())
)

class Company(Base):
    __tablename__ = 'company'

    id = Column(Integer, primary_key=True)
    ticker = Column(String(10), nullable=False, unique=True)
    name = Column(String(60), unique=True)
    locked = Column(Boolean, nullable=False, server_default=text("false"))
    delisted = Column(Boolean, nullable=False, index=True, server_default=text("false"))
    update_stamp = Column(DateTime(timezone=True), nullable=False, server_default=FetchedValue())
    
    exchanges = relationship("Exchange", secondary=t_company_exchange_relation, backref='companies')
    sectors = relationship("Sector", secondary=t_company_sector_relation)
    #balance_sheet_data = relationship('BalanceSheetData')
    #income_statement_data = relationship('IncomeStatementData')
    #cash_flow_statement_data = relationship('CashFlowStatementData')


class CountryInfo(Base):
    __tablename__ = 'country_info'

    id = Column(SmallInteger, primary_key=True)
    name = Column(String(60), nullable=False, unique=True)
    name_code = Column(String(10), nullable=False, unique=True)
    currency = Column(String(10), nullable=False)
    update_stamp = Column(DateTime(timezone=True), nullable=False, server_default=FetchedValue())

class StateInfo(Base):
    __tablename__ = 'state_info'

    id = Column(Integer, primary_key=True)
    country_info_id = Column(ForeignKey('country_info.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True)
    name = Column(String(60), nullable=False, unique=True)
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


class CompanyMiscInfo(Base):
    __tablename__ = 'company_misc_info'

    id = Column(BigInteger, primary_key=True)
    company_id = Column(ForeignKey('company.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True)
    occurence = Column(SmallInteger, nullable=True)
    shares_bas = Column(BigInteger)
    shares_dil = Column(BigInteger)
    date_recorded = Column(DateTime(timezone=True), nullable=False, index=True)
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