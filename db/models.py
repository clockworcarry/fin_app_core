# coding: utf-8
from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import *
from sqlalchemy.schema import *

import sys
import logging
import argparse

meta = MetaData(naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s"
      })

Base = declarative_base(metadata=meta)

class Company(Base):
    __tablename__ = 'company'

    id = Column(Integer, primary_key=True)
    ticker = Column(String(10), nullable=False, unique=True)
    name = Column(String(60), unique=True)
    locked = Column(Boolean, nullable=False, server_default=text("false"))
    delisted = Column(Boolean, nullable=False, index=True, server_default=text("false"))
    update_stamp = Column(DateTime(timezone=True), nullable=False, server_default=FetchedValue())


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
    country_info_id = Column(ForeignKey('country_info.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    name = Column(String(60), nullable=False, unique=True)
    update_stamp = Column(DateTime(timezone=True), nullable=False, server_default=FetchedValue())


class Sector(Base):
    __tablename__ = 'sector'

    id = Column(SmallInteger, primary_key=True)
    name_code = Column(String(50), nullable=False)
    name = Column(String(60), nullable=False)
    locked = Column(Boolean, nullable=False, server_default=text("false"))
    update_stamp = Column(DateTime(timezone=True), nullable=False, server_default=FetchedValue())


class Exchange(Base):
    __tablename__ = 'exchange'

    id = Column(SmallInteger, primary_key=True)
    country_info_id = Column(ForeignKey('country_info.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    name_code = Column(String(10), nullable=False, unique=True)
    name = Column(String(60), unique=True)
    update_stamp = Column(DateTime(timezone=True), nullable=False, server_default=FetchedValue())


class Industry(Base):
    __tablename__ = 'industry'

    id = Column(SmallInteger, primary_key=True)
    sector_id = Column(ForeignKey('sector.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    name = Column(String(60), nullable=False, unique=True)
    name_code = Column(String(60), nullable=False, unique=True)
    locked = Column(Boolean, nullable=False, server_default=text("false"))
    update_stamp = Column(DateTime(timezone=True), nullable=False, server_default=FetchedValue())


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


class Log(Base):
    __tablename__ = 'log'

    id = Column(Integer, primary_key=True)
    log_type = Column(String(20), nullable=False)
    message = Column(String(200))
    data = Column(LargeBinary)
    update_stamp = Column(DateTime(timezone=True), nullable=False, server_default=FetchedValue())


class CronJobRun(Base):
    __tablename__ = 'cron_job_run'

    id = Column(Integer, primary_key=True)
    log_id = Column(ForeignKey('log.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False) 
    success = Column(Boolean, nullable=False)


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


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('command', help="Command that will be executed. Valid: [create_database]")
    args, unknown = parser.parse_known_args()

    if args.command == 'create_database':
        create_database(sys.argv)
    else:
        print("Unknown command: " + sys.argv[1])
        sys.exit(0)