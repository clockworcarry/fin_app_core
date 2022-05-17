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
    prefix="/industries",
    tags=["industries"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)

class IndustriesApiModelOut(BaseModel):
    id: int
    sector_id: int
    name: str
    name_code: str
    locked: bool

@router.get("", response_model=List[IndustriesApiModelOut])
def get_all_industries():
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            query_res = session.query(Industry).all()
            
            resp = []
            
            for res in query_res:
                resp.append(IndustriesApiModelOut(id=res.id, sector_id=res.sector_id, name=res.name, name_code=res.name_code, locked=res.locked))
            
            return resp

    except ValidationError as val_err:
        raise HTTPException(status_code=500, detail=str(val_err))
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))

@router.get("/{sector_id}", response_model=List[IndustriesApiModelOut])
def get_all_sector_industries(sector_id):
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            query_res = session.query(Industry).filter(Industry.sector_id == sector_id).all()
            
            resp = []
            
            for res in query_res:
                resp.append(IndustriesApiModelOut(id=res.id, sector_id=res.sector_id, name=res.name, name_code=res.name_code, locked=res.locked))
            
            return resp

    except ValidationError as val_err:
        raise HTTPException(status_code=500, detail=str(val_err))
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))