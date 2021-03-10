from fastapi import APIRouter, status, HTTPException, File, UploadFile, Query
from typing import Optional, List
from pydantic import BaseModel, ValidationError, validator

from py_common_utils_gh.os_common_utils import setup_logger, default_log_formatter
from py_common_utils_gh.db_utils.db_utils import SqlAlchemySessionManager
from db.models import *
import numpy as np
import pandas as pd
from psycopg2 import *
from sqlalchemy import create_engine, select, insert, exists
from sqlalchemy.orm import sessionmaker

import datetime, base64

import simplejson as json

import api.config as api_config

router = APIRouter(
    prefix="/company",
    tags=["company"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)

class CompanyApiModelIn(BaseModel):
    ticker: str
    name: str
    locked: bool
    delisted: bool

class CompanyApiModelOut(BaseModel):
    id: int
    ticker: str
    name: str
    locked: bool
    delisted: bool

class CompanyApiModelUpdateIn(BaseModel):
    ticker: str = None
    name: str = None
    locked: bool = None
    delisted: bool = None

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=CompanyApiModelOut)
def save_company(company_body: CompanyApiModelIn):
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            company = Company(ticker=company_body.ticker, name=company_body.name, locked=company_body.locked, delisted=company_body.delisted)
            session.add(company)
            session.flush()
            ret = CompanyApiModelOut(id=company.id, ticker=company.ticker, name=company.name, locked=company.locked, delisted=company.delisted)
            return ret

    except ValidationError as val_err:
        raise HTTPException(status_code=500, detail=str(val_err))
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))

@router.post("/{company_id}", response_model=CompanyApiModelUpdateIn)
def update_company(company_body: CompanyApiModelIn):
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            db_company = session.query(Company).filter(Company.id == company_id).first()
            if db_company is None:
                raise HTTPException(status_code=500, detail="No company with id: " + company_id + " exists.")
            
                if company_body.ticker is not None:
                    db_company.ticker = company_body.ticker
                if company_body.name is not None:
                    db_company.name = company_body.name
                if company_body.locked is not None:
                    db_company.locked = company_body.locked
                if company_body.delisted is not None:
                    db_company.delisted = company_body.delisted

            session.flush()
            ret = CompanyApiModelOut(id=db_company.id, ticker=db_company.ticker, name=db_company.name, locked=db_company.locked, delisted=db_company.delisted)
            return ret

    except ValidationError as val_err:
        raise HTTPException(status_code=500, detail=str(val_err))
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))

@router.delete("/{company_id}")
def delete_company():
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            session.query(Company).filter(Company.id == company_id).delete()
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))

@router.post("/file", status_code=status.HTTP_201_CREATED)
def import_companies_from_file(csv_file: UploadFile = File(...), supplier_format: Optional[str] = Query(None, max_length=30)):
    try:
        input_companies_df = pd.read_csv(io.BytesIO(csv_file.file), compression='zip')
        
        unique_exchange_serie = pd.Series(input_companies_df['exchange'].unique())
        unique_exchange_serie = unique_exchange_serie.fillna('Missing')
        for elem in unique_exchange_serie:
            if session.query(exists().where(Exchange.name_code==elem)).scalar() is False:
                logger.warning("Unknown exchange detected: " + elem)
        
        #log unknown sectors so they can be manually added to db
        unique_sector_serie = pd.Series(input_companies_df['sector'].unique())
        unique_sector_serie = unique_sector_serie.fillna('Missing')
        for elem in unique_sector_serie:
            if session.query(exists().where(Sector.name==elem)).scalar() is False:
                logger.warning("Unknown sector detected: " + elem)

        #log unknown industries so they can be manually added to db
        unique_industry_serie = pd.Series(input_companies_df['industry'].unique())
        unique_industry_serie = unique_industry_serie.fillna('Missing')
        for elem in unique_industry_serie:
            if session.query(exists().where(Industry.name==elem)).scalar() is False:
                logger.warning("Unknown industry detected: " + elem)

        nb_rows = input_companies_df.shape[0]
        current_row = 0
        #save every new company in the db and update the ones that are not locked in the db
        for idx, row in input_companies_df.iterrows():
            if verbose:
                print("Current row: " + str(current_row) + " out of " + str(nb_rows) + ". Ticker: " + row['ticker'])
            row = row.fillna('Missing')
            #get sector_id for company to init new company with it
            tbl = Sector.__table__
            stmt = select([tbl.c.id, tbl.c.name]).where(tbl.c.name == row['sector']).limit(1)
            sector_res = session.connection().execute(stmt).first()
            if sector_res is None:
                logger.warning("None result when fetching first sector matching: " + row['sector'])
                continue
            else:
                exch_tbl = Exchange.__table__
                stmt = select([exch_tbl.c.id, exch_tbl.c.name]).where(exch_tbl.c.name_code == row['exchange']).limit(1)
                exch_res = session.connection().execute(stmt).first()
                if exch_res is not None:
                    if row['isdelisted'] == 'Y':
                        row['isdelisted'] = True
                    elif row['isdelisted'] == 'N':
                        row['isdelisted'] = False
                    else:
                        logger.critical("Unknown value in delisted column: " + row['isdelisted'])
                        continue
                    
                    '''db_company = session.query(Company).filter(Company.name == row['name']).first()
                    if db_company is not None and not db_company.locked and db_company.ticker != row['ticker']: # company ticker was changed but name stayed the same
                        logger.info("Company with name " + row['name'] + " ticker changed from " + db_company.ticker + " to " + row['ticker'])
                        db_company_retry = session.query(Company).filter(Company.ticker == row['ticker']).first() # ticker already taken, this probably means company changed name AND ticker
                        if db_company_retry is not None and db_company.delisted:
                            logger.warning("Deleting existing company with ticker: " + db_company.ticker + ". Probably simultaneous change of name and ticker. Validate.")
                            session.delete(db_company)
                        else:
                            db_company.ticker = row['ticker']'''
                        

                    db_company = session.query(Company).filter(Company.ticker == row['ticker']).first()
                    if db_company is not None and not db_company.locked and db_company.name != row['name']: # company name was changed but ticker stayed the same
                        '''logger.info("Company with ticker " + row['ticker'] + " name changed from " + db_company.name + " to " + row['name'])
                        db_company.name = row['name']'''
                        session.delete(db_company)
                        db_company = None

                    if db_company is None: #insert
                        if session.query(exists().where(Company.name==row['name'])).scalar() is False: #it is possible that there a company is listed with same name with different tickers ...
                            company = Company(ticker=row['ticker'], name=row['name'], delisted=row['isdelisted'])
                            session.add(company)
                            session.flush() #force company id creation
                            stmt = t_company_exchange_relation.insert()
                            session.connection().execute(stmt, company_id=company.id, exchange_id=exch_res.id) #insert company and exch id in the relation table
                            stmt = t_company_sector_relation.insert()
                            session.connection().execute(stmt, company_id=company.id, sector_id=sector_res.id) #insert company and sector id in the relation table
                        else:
                            logger.warning("Company already exists: " + row['name'])
                    elif not db_company.locked: #update
                        db_company.name = row['name']
                        db_company.delisted = row['isdelisted']
                        logger.info("The following ticker was updated in the company table: " + db_company.ticker)
            
            current_row += 1
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))