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

class CompanyGroupModelOutShort(BaseModel):
    id: int
    name_code: str
    name: str
    description: str = None
    industry_id: int = None

class CompanyApiModelOut(BaseModel):
    id: int
    ticker: str
    name: str
    locked: bool
    groups: List[CompanyGroupModelOutShort] = None
    delisted: bool

class CompanyBusinessOrProductOut(BaseModel):
    id: int
    code: str
    display_name: str
    company_info: CompanyApiModelOut
    

class CompanyGroupModelOut(BaseModel):
    id: int
    name_code: str
    name: str
    description: str = None
    industry_id: int = None
    business_segments: List[CompanyBusinessOrProductOut] = []

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
    industry_id: int = None
    company_business_or_product_ids: List[int]

class CompanyApiModelIn(BaseModel):
    ticker: str
    name: str
    locked: bool
    delisted: bool
    group_id: int

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

def get_company_groups_session(bop_id, session, load_bops = False):
    manager = SqlAlchemySessionManager()
    
    ret = []
    db_ret = None
    if load_bops:
        if bop_id is None:    
            db_ret = session.query(CompanyGroup, CompanyGroupRelation, CompanyBusinessOrProduct, Company) \
                .join(CompanyGroupRelation, CompanyGroupRelation.group_id == CompanyGroup.id) \
                .join(CompanyBusinessOrProduct, CompanyGroupRelation.company_business_or_product_id == CompanyBusinessOrProduct.id) \
                .join(Company, CompanyBusinessOrProduct.company_id == Company.id) \
                .all()
            

        else:
            #.filter(CompanyGroupRelation.company_business_or_product_id == bop_id) \
            db_ret = session.query(CompanyGroup, CompanyGroupRelation, CompanyBusinessOrProduct, Company) \
                .join(CompanyGroupRelation, CompanyGroupRelation.group_id == CompanyGroup.id) \
                .join(CompanyBusinessOrProduct, CompanyGroupRelation.company_business_or_product_id == CompanyBusinessOrProduct.id) \
                .join(Company, CompanyBusinessOrProduct.company_id == Company.id) \
                .all()
            


        
    
    else:
        if bop_id is None:
            db_ret = session.query(CompanyGroup, CompanyGroupRelation, CompanyBusinessOrProduct, Company) \
                        .join(CompanyGroupRelation, CompanyGroupRelation.group_id == CompanyGroup.id) \
                        .all()
        else:
            db_ret = session.query(CompanyGroup, CompanyGroupRelation, CompanyBusinessOrProduct, Company) \
                        .join(CompanyGroupRelation, CompanyGroupRelation.group_id == CompanyGroup.id) \
                        .filter(CompanyGroupRelation.company_business_or_product_id == bop_id) \
                        .all() 

    for dr in db_ret:
        skip = False
        for r in ret:
            if r.id == dr[0].id:
                skip = True

        if skip:
            continue
                
        segments = []
        for dr_inner in db_ret:
            if dr[0].id == dr_inner[0].id:
                cpny_info = CompanyApiModelOut(id=dr_inner[3].id, ticker=dr_inner[3].ticker, name=dr_inner[3].name, locked=dr_inner[3].locked, delisted=dr_inner[3].delisted)
                segments.append(CompanyBusinessOrProductOut(id=dr_inner[2].id, code=dr_inner[2].code, display_name=dr_inner[2].display_name, company_info=cpny_info))

        camo = CompanyGroupModelOut(id=dr[0].id, name_code=dr[0].name_code, name=dr[0].name, industry_id=dr[0].industry_id, business_segments=segments)
        ret.append(camo)

    if bop_id is not None:
        if isinstance(bop_id, str):
            bop_id = int(bop_id)
        grps_with_bop = []
        for r in ret:
            for bop in r.business_segments:
                if bop.id == bop_id:
                    grps_with_bop.append(r.id)

        ret = [res for res in ret if res.id in grps_with_bop]

    return ret

def get_company_groups(bop_id, load_bops = False):
    manager = SqlAlchemySessionManager()
    with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
        grps = get_company_groups_session(bop_id, session, load_bops)
        session.expunge_all()
        return grps


def get_group_bops_session(grp_id, session):
    db_ret = session.query(Company, CompanyBusinessOrProduct) \
                    .join(CompanyGroupRelation, CompanyGroupRelation.company_business_or_product_id == CompanyBusinessOrProduct.id) \
                    .join(Company, Company.id == CompanyBusinessOrProduct.company_id) \
                    .filter(CompanyGroupRelation.group_id == grp_id) \
                    .all()
    
    ret = []
    for dr in db_ret:
        cpny_info = CompanyApiModelOut(id=dr[0].id, ticker=dr[0].ticker, name=dr[0].name, locked=dr[0].locked, delisted=dr[0].delisted)
        ret.append(CompanyBusinessOrProductOut(id=dr[1].id, code=dr[1].code, display_name=dr[1].display_name, company_info=cpny_info))
        
    return ret

def get_group_bops(grp_id):
    manager = SqlAlchemySessionManager()
    with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
        return get_group_bops_session(grp_id, session)


def get_bop_info_session(bop_id, session):
    db_ret = session.query(Company, CompanyBusinessOrProduct) \
                    .join(Company, CompanyBusinessOrProduct.company_id == Company.id) \
                    .filter(CompanyBusinessOrProduct.id == bop_id) \
                    .all()
    
    ret = []
    for dr in db_ret:
        cpny_info = CompanyApiModelOut(id=dr[0].id, ticker=dr[0].ticker, name=dr[0].name, locked=dr[0].locked, delisted=dr[0].delisted)
        ret.append(CompanyBusinessOrProductOut(id = dr[1].id, code=dr[1].code, display_name=dr[1].display_name, company_info=cpny_info))

    return ret

def get_bop_info(bop_id):
    manager = SqlAlchemySessionManager()
    with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
        return get_bop_info_session(bop_id, session)
        

def get_bop_info_company(cpny_id):
    manager = SqlAlchemySessionManager()
    with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
        bops = session.query(CompanyBusinessOrProduct).filter(CompanyBusinessOrProduct.company_id == cpny_id).all()

        ret = []
        for b in bops:
            tmp = get_bop_info_session(b.id, session)
            for t in tmp:
                 ret.append(t)

        return ret


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
                grps_out.append(CompanyGroupModelOut(id=grp.id, name_code=grp.name_code, name=grp.name, description=grp.description, industry_id=grp.industry_id))

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
            
            ret = get_company_groups(None, True)
  
            return ret

    except ValidationError as val_err:
        raise HTTPException(status_code=500, detail=str(val_err))
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))

@router.get("/groups/{bop_id}", response_model=List[CompanyGroupModelOut])
def get_groups(bop_id):
    try:
        ret = get_company_groups(bop_id, True)
  
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

@router.post("/group/{group_id}/{bop_id}", response_model=CompanyGroupModelOut)
def add_bop_to_group(group_id, bop_id):
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            db_grp = session.query(CompanyGroup).filter(CompanyGroup.id == group_id).first()
            if db_grp is None:
                raise HTTPException(status_code=500, detail="No company group with id: " + group_id + " exists.")
            
            session.add(CompanyGroupRelation(company_business_or_product_id=bop_id, group_id=group_id))

            bops = get_group_bops_session(group_id, session)
            

            return CompanyGroupModelOut(id=db_grp.id, name_code=db_grp.name_code, name=db_grp.name, description=db_grp.description, industry_id=db_grp.industry_id, business_segments=bops)

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
            ret = get_bop_info_company(company_id)
            return ret

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




