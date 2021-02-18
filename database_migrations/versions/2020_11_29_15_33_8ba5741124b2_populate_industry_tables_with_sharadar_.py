"""populate industry tables with sharadar values

Revision ID: 8ba5741124b2
Revises: 32dbf49e0390
Create Date: 2020-11-29 15:33:38.901237

"""
from alembic import op
from sqlalchemy import *
from sqlalchemy import orm
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import *
from sqlalchemy.schema import *
import pandas as pd

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
    ticker = Column(String(5), nullable=False, unique=True)
    name = Column(String(60), unique=True)
    locked = Column(Boolean, nullable=False, server_default=text("false"))
    delisted = Column(Boolean, nullable=False, index=True, server_default=text("false"))
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

class CountryInfo(Base):
    __tablename__ = 'country_info'

    id = Column(SmallInteger, primary_key=True)
    name = Column(String(60), nullable=False, unique=True)
    name_code = Column(String(10), nullable=False, unique=True)
    currency = Column(String(10), nullable=False)
    update_stamp = Column(DateTime(timezone=True), nullable=False, server_default=FetchedValue())


# revision identifiers, used by Alembic.
revision = '8ba5741124b2'
down_revision = '32dbf49e0390'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    session = orm.Session(bind=bind)

    usa_country_info = session.query(CountryInfo).filter(CountryInfo.name_code == 'USA').first()

    #exchanges
    session.add(Exchange(country_info_id=usa_country_info.id, name_code='NASDAQ', name='NASDAQ'))
    session.add(Exchange(country_info_id=usa_country_info.id, name_code='OTC', name='Over the counter'))
    session.add(Exchange(country_info_id=usa_country_info.id, name_code='NYSEMKT', name='New York Small Cap Equity Market'))
    session.add(Exchange(country_info_id=usa_country_info.id, name_code='NYSE', name='New York Stock Exchange'))
    session.add(Exchange(country_info_id=usa_country_info.id, name_code='NYSEARCA', name='New York Stock Exchange Arca'))
    session.add(Exchange(country_info_id=usa_country_info.id, name_code='BATS', name='Bats Global Markets'))

    #sectors
    tech_sector = Sector(name_code='Tech', name='Technology')
    cyclical_sector = Sector(name_code='Cyclical', name='Consumer Cyclical')
    fin_sector = Sector(name_code='Finance', name='Financial Services')
    comm_sector = Sector(name_code='Comm', name='Communication Services')
    utilities_sector = Sector(name_code='Utilities', name='Utilities')
    defensive_sector = Sector(name_code='Defensive', name='Consumer Defensive')
    missing_sector = Sector(name_code='Missing', name='Missing')
    health_sector = Sector(name_code='Health', name='Healthcare')
    real_estate_sector = Sector(name_code='Real Estate', name='Real Estate')
    industrials_sector = Sector(name_code='Industrials', name='Industrials')
    energy_sector = Sector(name_code='Energy', name='Energy')
    materials_sector = Sector(name_code='Materials', name='Basic Materials')

    session.add(tech_sector)
    session.add(cyclical_sector)
    session.add(fin_sector)
    session.add(comm_sector)
    session.add(utilities_sector)
    session.add(defensive_sector)
    session.add(missing_sector)
    session.add(health_sector)
    session.add(real_estate_sector)
    session.add(industrials_sector)
    session.add(energy_sector)
    session.add(materials_sector)

    session.flush()

    df = pd.read_csv("/home/ghelie/fin_app/companies.csv")
    for idx, row in df.iterrows():
        row = row.fillna('Missing')
        if session.query(exists().where(Industry.name==row['industry'])).scalar() is False:
            sector = session.query(Sector).filter(Sector.name == row['sector']).first()
            if sector is not None:
                session.add(Industry(sector_id=sector.id, name=row['industry'], name_code=row['industry']))

    session.commit()
    

def downgrade():
    pass
