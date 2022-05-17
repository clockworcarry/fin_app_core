from fastapi import APIRouter, status, HTTPException
from typing import Optional, List
from pydantic import BaseModel, ValidationError, validator

from py_common_utils_gh.os_common_utils import setup_logger, default_log_formatter
from py_common_utils_gh.db_utils.db_utils import SqlAlchemySessionManager
from db.models import *
import numpy as np
from psycopg2 import *
from sqlalchemy import create_engine, select, insert, exists
from sqlalchemy.orm import sessionmaker

import datetime, base64

import simplejson as json

import api.config as api_config

router = APIRouter(
    prefix="/industry",
    tags=["industry"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)

class IndustrySaveModelIn(BaseModel):
    sector_id: int
    name: str
    name_code: str
    locked: bool

class IndustrySaveModelOut(BaseModel):
    id: int
    sector_id: int
    name: str
    name_code: str
    locked: bool



@router.post("", status_code=status.HTTP_201_CREATED, response_model=IndustrySaveModelOut)
def create_industry(body: IndustrySaveModelIn):
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            new_industry = Industry(sector_id=body.sector_id, name=body.name, name_code=body.name_code, locked=body.locked)
            session.add(new_industry)
            session.flush()
            
            return IndustrySaveModelOut(id=new_industry.id, sector_id=new_industry.sector_id, name=new_industry.name, name_code=new_industry.name_code, locked=new_industry.locked)
    
    except ValidationError as val_err:
        raise HTTPException(status_code=500, detail=str(val_err))
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))

@router.put("/{industry_id}", status_code=status.HTTP_200_OK, response_model=IndustrySaveModelOut)
def update_industry(industry_id, body: IndustrySaveModelIn):
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            db_industry = Industry(id=industry_id, sector_id=body.sector_id, name=body.name, name_code=body.name_code, locked=body.locked)
            session.add(db_industry)
            
            return IndustrySaveModelOut(id=db_industry.id, sector_id=db_industry.sector_id, name=db_industry.name, name_code=db_industry.name_code, locked=db_industry.locked)
    
    except ValidationError as val_err:
        raise HTTPException(status_code=500, detail=str(val_err))
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))