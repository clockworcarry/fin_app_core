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

class CompanyGroupModelOut(BaseModel):
    id: int
    name_code: str
    name: str
    description: str = None
    industry_id: int

class CompanyGroupModelIn(BaseModel):
    name_code: str
    name: str
    description: str = None
    industry_id: int

class CompanySaveGroupModelIn(BaseModel):
    name_code: str
    name: str
    description: Optional[str] = None
    industry_id: int = None
    company_business_or_product_ids: List[int]

class CompanySaveGroupModelOut(BaseModel):
    id: int
    name_code: str
    name: str
    description: str
    industry_id: int
    company_business_or_product_ids: List[int]

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
    groups: List[CompanyGroupModelOut]
    delisted: bool

class CompanyBusinessOrProductOut(BaseModel):
    id: int
    code: str
    display_name: str
    company_id: int

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

class CompanyUpdateGroupIdModelIn(BaseModel):
    group_id: int

class CompanyGroupsModelIn(BaseModel):
    page_limit: int = 200
    page: int = 0

def get_company_groups_session(bop_id, session):
    manager = SqlAlchemySessionManager()
    grps = session.query(CompanyGroup) \
                .join(CompanyGroupRelation, CompanyGroupRelation.group_id == CompanyGroup.id) \
                .filter(CompanyGroupRelation.company_business_or_product_id == bop_id) \
                .all()
    return grps

def get_company_groups(bop_id):
    manager = SqlAlchemySessionManager()
    with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
        grps = get_company_groups_session(bop_id, session)
        session.expunge_all()
        return grps

def get_company_default_bop(company_id, company_ticker, session):
    return session.query(CompanyBusinessOrProduct).filter(and_(CompanyBusinessOrProduct.company_id == company_id, CompanyBusinessOrProduct.code == company_ticker + "_default")).first()


@router.get("/{ticker}", status_code=status.HTTP_200_OK, response_model=CompanyApiModelOut)
def get_company_by_ticker(ticker):
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            company = session.query(Company).filter(Company.ticker == ticker).first()
            if company is None:
                raise HTTPException(status_code=500, detail="No company with ticker: " + ticker + " exists.")
            
            default_bop = get_company_default_bop(company.id, company.ticker, session)
            if default_bop is None:
                raise HTTPException(status_code=500, detail="No default business or product for: " + ticker + " exists.")
            
            company_grps = get_company_groups_session(default_bop.id, session)

            grps_out = []
            for grp in company_grps:
                grps_out.append(CompanyGroupModelOut(id = grp.id, name_code=grp.name_code, name=grp.name))

            return CompanyApiModelOut(id=company.id, ticker=company.ticker, name=company.name, locked=company.locked, delisted=company.delisted, groups=grps_out)

    except ValidationError as val_err:
        raise HTTPException(status_code=500, detail=str(val_err))
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))


@router.post("/groups", response_model=List[CompanyGroupModelOut])
def get_groups(body: CompanyGroupsModelIn):
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            if body.page_limit > 200:
                body.page_limit = 200
            
            groups = session.query(CompanyGroup).limit(body.page_limit).offset(body.page)

            ret = []
            for grp in groups:
                camo = CompanyGroupModelOut(id=grp.id, name_code=grp.name_code, name=grp.name, industry_id=grp.industry_id)
                ret.append(camo)
            
            return ret

    except ValidationError as val_err:
        raise HTTPException(status_code=500, detail=str(val_err))
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))

@router.get("/groups/{bop_id}", response_model=List[CompanyGroupModelOut])
def get_groups(bop_id):
    try:
        groups = get_company_groups(bop_id)

        ret = []
        for grp in groups:
            camo = CompanyGroupModelOut(id=grp.id, name_code=grp.name_code, name=grp.name, description=grp.description, industry_id=grp.industry_id)
            ret.append(camo)
        
        return ret

    except ValidationError as val_err:
        raise HTTPException(status_code=500, detail=str(val_err))
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))


@router.post("/group", response_model=CompanySaveGroupModelOut)
def create_group(body: CompanySaveGroupModelIn):
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            new_grp = CompanyGroup(name_code=body.name_code, name=body.name, description=body.description, industry_id=body.industry_id)
            session.add(new_grp)
            session.flush()

            for bop_id in body.company_business_or_product_ids:
                session.add(CompanyGroupRelation(company_business_or_product_id=bop_id, group_id=new_grp.id))

            out_desc = new_grp.description
            if out_desc is None:
                out_desc = ''


            return CompanySaveGroupModelOut(id=new_grp.id, name_code=new_grp.name_code, name=new_grp.name, description=out_desc, industry_id=new_grp.industry_id, company_business_or_product_ids=body.company_business_or_product_ids)

    except ValidationError as val_err:
        raise HTTPException(status_code=500, detail=str(val_err))
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))

@router.put("/group/{group_id}", response_model=CompanyGroupModelOut)
def update_group(group_id, body: CompanyGroupModelIn):
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            new_grp = CompanyGroup(id=group_id, name_code=body.name_code, name=body.name, description=body.description, industry_id=body.industry_id)
            session.add(new_grp)
            
            db_relations = session.query(CompanyGroupRelation).filter(CompanyGroupRelation.group_id == group_id)

            for db_rel in db_relations:
                found = False
                for body_rel in body.company_business_or_product_ids:
                    if db_rel.company_business_or_product_id == body_rel.company_business_or_product_id:
                        found = True
                        break
                if not found:
                    session.delete(db_rel)

            for bop_id in body.company_business_or_product_ids:
                session.add(CompanyGroupRelation(company_business_or_product_id=bop_id, group_id=new_grp.id))

            return CompanyGroupModelOut(id=new_grp.id, name_code=new_grp.name_code, name=new_grp.name, description=new_grp.description, industry_id=new_grp.industry_id, company_business_or_product_ids=body.company_business_or_product_ids)

    except ValidationError as val_err:
        raise HTTPException(status_code=500, detail=str(val_err))
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))



'''@router.get("/group/{grp_id}", response_model=CompanyGroupModelOut)
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
        raise HTTPException(status_code=500, detail=str(gen_ex))'''

        

'''@router.patch("/group/{company_id}", response_model=CompanyApiModelOut)
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
        raise HTTPException(status_code=500, detail=str(gen_ex))'''

'''@router.delete("/group/{group_id}")
def delete_group():
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            session.query(CompanyGroup).filter(CompanyGroup.id == group_id).delete()
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))'''

'''@router.post("/", status_code=status.HTTP_201_CREATED, response_model=CompanyApiModelOut)
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
def update_company(company_id, company_body: CompanyApiModelIn):
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
        raise HTTPException(status_code=500, detail=str(gen_ex))'''

'''@router.post("/{company_id}", response_model=CompanyApiModelUpdateIn)
def add_business_or_product_to_company(company_body: CompanyApiModelIn):
    pass
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
        raise HTTPException(status_code=500, detail=str(gen_ex))'''

@router.get("/businessOrProduct/{company_id}", status_code=status.HTTP_200_OK, response_model=List[CompanyBusinessOrProductOut])
def get_company_businesses_and_products(company_id):
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            bops = session.query(CompanyBusinessOrProduct).filter(CompanyBusinessOrProduct.company_id == company_id).all()

            resp = []

            for bop in bops:
                resp.append(CompanyBusinessOrProductOut(id=bop.id, code=bop.code, display_name=bop.display_name, company_id=bop.company_id))

            return resp

    except ValidationError as val_err:
        raise HTTPException(status_code=500, detail=str(val_err))
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))



'''@router.delete("/{company_id}")
def delete_company():
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            session.query(Company).filter(Company.id == company_id).delete()
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))'''




