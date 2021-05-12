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
    group_id: int

class CompanyApiModelOut(BaseModel):
    id: int
    ticker: str
    name: str
    locked: bool
    group_id: int
    delisted: bool

class CompanyApiModelUpdateIn(BaseModel):
    ticker: str = None
    name: str = None
    locked: bool = None
    delisted: bool = None

class CompanyImportApiModelOut(BaseModel):
    companies_with_null_exchange: List[str] = []
    companies_with_null_sector: List[str] = []
    companies_with_null_industry: List[str] = []
    companies_with_unknown_sector: List[str] = []
    companies_with_name_change: List[str] = []
    companies_with_ticker_change: List[str] = []

class CompanyProductsModelOut(BaseModel):
    id: int
    code: str
    display_name: str

class CompanyGroupModelOut(BaseModel):
    id: int
    name_code: str
    name: str

class CompanyUpdateGroupIdModelIn(BaseModel):
    group_id: int

@router.get("/groups", response_model=List[CompanyGroupModelOut])
def get_groups():
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            groups = session.query(CompanyGroup).all()

            ret = []
            for grp in groups:
                camo = CompanyGroupModelOut(id=grp.id, grp.name_code, grp.name)
                ret.append(camo)
            
            return ret

    except ValidationError as val_err:
        raise HTTPException(status_code=500, detail=str(val_err))
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))

@router.get("/group/{grp_id}", response_model=CompanyGroupModelOut)
def get_group():
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            grp = session.query(CompanyGroup).filter(CompanyGroup.id == grp_id).all()
            if grp is None:
                raise HTTPException(status_code=500, "No company group with id: " + grp_id + " exists.")

            ret = CompanyGroupModelOut(id=grp.id, name_code=grp.name_code, name=grp.name)
            return ret

    except ValidationError as val_err:
        raise HTTPException(status_code=500, detail=str(val_err))
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))

@router.patch("/group/{company_id}", response_model=CompanyApiModelOut)
def update_company_group_id(body: CompanyUpdateGroupIdModelIn):
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            company = session.query(Company).filter(Company.id == company_id).first()
            if company is None:
                raise HTTPException(status_code=500, "No company with id: " + company_id + " exists.")
            
            company.group_id = body.group_id
            ret = CompanyApiModelOut(id=company.id.id, ticker=company.ticker, name=company.name, delisted=company.delisted, locked=company.locked, group_id=company.group_id)
            return ret

    except ValidationError as val_err:
        raise HTTPException(status_code=500, detail=str(val_err))
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))

@router.delete("/group/{group_id}")
def delete_group():
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            session.query(CompanyGroup).filter(CompanyGroup.id == group_id).delete()
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))

@router.get("/{ticker}", status_code=status.HTTP_201_CREATED, response_model=CompanyApiModelOut)
def get_company_by_ticker(company_body: CompanyApiModelIn):
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            company = session.query(Company).filter(Company.ticker == ticker).first()
            if company is None:
                raise HTTPException(status_code=500, "No company with ticker: " + ticker + " exists.")

            ret = CompanyApiModelOut(id=company.id, ticker=company.ticker, name=company.name, locked=company.locked, delisted=company.delisted, group_id=company.group_id)
            return ret

    except ValidationError as val_err:
        raise HTTPException(status_code=500, detail=str(val_err))
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=CompanyApiModelOut)
def save_company(company_body: CompanyApiModelIn):
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            company = Company(ticker=company_body.ticker, name=company_body.name, locked=company_body.locked, delisted=company_body.delisted, group_id=company_body.group_id)
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



