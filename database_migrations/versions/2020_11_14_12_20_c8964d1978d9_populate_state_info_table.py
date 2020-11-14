"""populate state_info_table

Revision ID: c8964d1978d9
Revises: b12948034865
Create Date: 2020-11-14 12:20:18.693631

"""
from alembic import op
from sqlalchemy import Boolean, Column, ForeignKey, Integer, SmallInteger, String, Table, text, MetaData, orm
from sqlalchemy.ext.declarative import declarative_base

meta = MetaData(naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s"
      })

Base = declarative_base(metadata=meta)

class CountryInfo(Base):
    __tablename__ = 'country_info'

    id = Column(SmallInteger, primary_key=True)
    name = Column(String(60), nullable=False, unique=True)
    currency = Column(String(10), nullable=False)

class StateInfo(Base):
    __tablename__ = 'state_info'

    id = Column(Integer, primary_key=True)
    country_info_id = Column(ForeignKey('country_info.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    name = Column(String(60), nullable=False, unique=True)


# revision identifiers, used by Alembic.
revision = 'c8964d1978d9'
down_revision = 'b12948034865'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    session = orm.Session(bind=bind)

    #Add usa to countries table and query to get an id
    session.add(CountryInfo(name='United States of America', currency='USD'))
    usa = session.query(CountryInfo).filter(CountryInfo.name=='United States of America').first()

    #add states and set their foreign key value to usa id
    session.add(StateInfo(country_info_id=usa.id, name='Alaska'))
    session.add(StateInfo(country_info_id=usa.id, name='Alabama'))
    session.add(StateInfo(country_info_id=usa.id, name='Arkansas'))
    session.add(StateInfo(country_info_id=usa.id, name='Arizona'))
    session.add(StateInfo(country_info_id=usa.id, name='California'))
    session.add(StateInfo(country_info_id=usa.id, name='Colorado'))
    session.add(StateInfo(country_info_id=usa.id, name='Connecticut'))
    session.add(StateInfo(country_info_id=usa.id, name='District of Columbia'))
    session.add(StateInfo(country_info_id=usa.id, name='Delaware'))
    session.add(StateInfo(country_info_id=usa.id, name='Florida'))
    session.add(StateInfo(country_info_id=usa.id, name='Georgia'))
    session.add(StateInfo(country_info_id=usa.id, name='Hawaii'))
    session.add(StateInfo(country_info_id=usa.id, name='Iowa'))
    session.add(StateInfo(country_info_id=usa.id, name='Idaho'))
    session.add(StateInfo(country_info_id=usa.id, name='Illinois'))
    session.add(StateInfo(country_info_id=usa.id, name='Indiana'))
    session.add(StateInfo(country_info_id=usa.id, name='Kansas'))
    session.add(StateInfo(country_info_id=usa.id, name='Kentucky'))
    session.add(StateInfo(country_info_id=usa.id, name='Lousiana'))
    session.add(StateInfo(country_info_id=usa.id, name='Massachusetts'))
    session.add(StateInfo(country_info_id=usa.id, name='Maryland'))
    session.add(StateInfo(country_info_id=usa.id, name='Maine'))
    session.add(StateInfo(country_info_id=usa.id, name='Michigan'))
    session.add(StateInfo(country_info_id=usa.id, name='Minnesota'))
    session.add(StateInfo(country_info_id=usa.id, name='Missouri'))
    session.add(StateInfo(country_info_id=usa.id, name='Mississippi'))
    session.add(StateInfo(country_info_id=usa.id, name='Montana'))
    session.add(StateInfo(country_info_id=usa.id, name='North Carolina'))
    session.add(StateInfo(country_info_id=usa.id, name='North Dakota'))
    session.add(StateInfo(country_info_id=usa.id, name='Nebraska'))
    session.add(StateInfo(country_info_id=usa.id, name='New Hampshire'))
    session.add(StateInfo(country_info_id=usa.id, name='New Jersey'))
    session.add(StateInfo(country_info_id=usa.id, name='New Mexico'))
    session.add(StateInfo(country_info_id=usa.id, name='Nevada'))
    session.add(StateInfo(country_info_id=usa.id, name='New York'))
    session.add(StateInfo(country_info_id=usa.id, name='Ohio'))
    session.add(StateInfo(country_info_id=usa.id, name='Oklahoma'))
    session.add(StateInfo(country_info_id=usa.id, name='Oregon'))
    session.add(StateInfo(country_info_id=usa.id, name='Pennsylvania'))
    session.add(StateInfo(country_info_id=usa.id, name='Puerto Rico'))
    session.add(StateInfo(country_info_id=usa.id, name='Rhode Island'))
    session.add(StateInfo(country_info_id=usa.id, name='South Carolina'))
    session.add(StateInfo(country_info_id=usa.id, name='South Dakota'))
    session.add(StateInfo(country_info_id=usa.id, name='Tennessee'))
    session.add(StateInfo(country_info_id=usa.id, name='Texas'))
    session.add(StateInfo(country_info_id=usa.id, name='Utah'))
    session.add(StateInfo(country_info_id=usa.id, name='Virginia'))
    session.add(StateInfo(country_info_id=usa.id, name='Vermont'))
    session.add(StateInfo(country_info_id=usa.id, name='Washington'))
    session.add(StateInfo(country_info_id=usa.id, name='Wisconsin'))
    session.add(StateInfo(country_info_id=usa.id, name='West Virginia'))
    session.add(StateInfo(country_info_id=usa.id, name='Wyoming'))

    session.commit()


def downgrade():
    pass

if __name__ == "__main__":
    upgrade()
