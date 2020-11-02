# coding: utf-8
from sqlalchemy import Boolean, Column, ForeignKey, Integer, MetaData, SmallInteger, String, Table, text

metadata = MetaData()


t_company = Table(
    'company', metadata,
    Column('id', Integer, primary_key=True, server_default=text("nextval('\"Company_id_seq\"'::regclass)")),
    Column('ticker', String(5), nullable=False, unique=True),
    Column('name', String(60), unique=True),
    Column('locked', Boolean, nullable=False, index=True, server_default=text("false"))
)


t_country_info = Table(
    'country_info', metadata,
    Column('id', Integer, primary_key=True, server_default=text("nextval('country_info_id_seq'::regclass)")),
    Column('name', String(60), nullable=False, unique=True),
    Column('currency', String(10), nullable=False)
)


t_exchange = Table(
    'exchange', metadata,
    Column('id', SmallInteger, primary_key=True, server_default=text("nextval('exchange_id_seq'::regclass)")),
    Column('country_info_id', ForeignKey('country_info.id', ondelete='CASCADE', onupdate='CASCADE')),
    Column('name_code', String(10), nullable=False, unique=True),
    Column('name', String(60), unique=True)
)


t_company_exchange_relation = Table(
    'company_exchange_relation', metadata,
    Column('company_id', ForeignKey('company.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True, nullable=False),
    Column('exchange_id', ForeignKey('exchange.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True, nullable=False)
)