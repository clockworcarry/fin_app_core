from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import *
from sqlalchemy.schema import *

from db.base_models import Base, meta

'''class MacroDevelopment(Base):
    __tablename__ = 'macro_development'

    id = Column(BigInteger, primary_key=True)
    display_name = Column(String(120), nullable=False)
    dev_type = Column(SmallInteger, nullable=False, index=True) #conference, devcon, news release, interview, etc.
    data_type = Column(SmallInteger, nullable=False, index=True) #png, link, text, etc.
    data = Column(LargeBinary)
    date_recorded = Column(DateTime(timezone=True), nullable=False, index=True)'''