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
    prefix="/sector",
    tags=["sector"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)

class SectorSaveModelIn(BaseModel):
    name: str
    name_code: str
    locked: bool

class SectorSaveModelOut(BaseModel):
    id: int
    name: str
    name_code: str
    locked: bool



@router.post("", status_code=status.HTTP_201_CREATED, response_model=SectorSaveModelOut)
def create_sector(body: SectorSaveModelIn):
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            new_sector = Sector(name=body.name, name_code=body.name_code, locked=body.locked)
            session.add(new_sector)
            session.flush()
            
            return SectorSaveModelOut(id=new_sector.id, name=new_sector.name, name_code=new_sector.name_code, locked=new_sector.locked)
    
    except ValidationError as val_err:
        raise HTTPException(status_code=500, detail=str(val_err))
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))

@router.put("/{sector_id}", status_code=status.HTTP_200_OK, response_model=SectorSaveModelOut)
def update_sector(sector_id, body: SectorSaveModelIn):
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            db_sector = Sector(id=sector_id, name=body.name, name_code=body.name_code, locked=body.locked)
            session.add(db_sector)
            
            return SectorSaveModelOut(id=db_sector.id, name=db_sector.name, name_code=db_sector.name_code, locked=db_sector.locked)
    
    except ValidationError as val_err:
        raise HTTPException(status_code=500, detail=str(val_err))
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))