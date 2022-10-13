from urllib.request import Request
from fastapi import APIRouter, status, HTTPException, Response, Request
from typing import Optional, List
from pydantic import BaseModel, ValidationError, validator
from starlette.status import HTTP_204_NO_CONTENT, HTTP_201_CREATED, HTTP_401_UNAUTHORIZED

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
import api.constants as api_constants
import core.constants as core_constants

router = APIRouter(
    prefix="/" + api_constants.app_name + "/" + api_constants.version + "/industry",
    tags=["industry"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)

class IndustrySaveModelIn(BaseModel):
    sector_id: int
    name: str
    name_code: str

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_industry(body: IndustrySaveModelIn, request: Request):
    try:
        if request.state.rctx.user_id != core_constants.system_user_id:
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Only system user can create a new industry. Other users should create company groups.")

        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            new_industry = Industry(sector_id=body.sector_id, name=body.name, name_code=body.name_code)
            session.add(new_industry)
            
        return Response(status_code=HTTP_201_CREATED)
    
    except ValidationError as val_err:
        raise HTTPException(status_code=500, detail=str(val_err))
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))

@router.put("/{industry_id}", status_code=status.HTTP_200_OK)
def update_industry(industry_id, body: IndustrySaveModelIn, request: Request):
    try:
        if request.state.rctx.user_id != core_constants.system_user_id:
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Only system user can update an industry. Other users should create company groups.")

        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            db_industry = session.query(Industry).filter(Industry.id == industry_id).first()
            if db_industry is None:
                raise Exception("Could not load industry with id: " + str(industry_id))
            
        return Response(status_code=HTTP_204_NO_CONTENT)
    
    except ValidationError as val_err:
        raise HTTPException(status_code=500, detail=str(val_err))
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))

@router.delete("/{industry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sector(industry_id, request: Request):
    try:
        if request.state.rctx.user_id != core_constants.system_user_id:
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Only system user can delete an industry.")

        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            db_industry = session.query(Industry).filter(Industry.id == industry_id).first()
            if db_industry is None:
                raise Exception("Could not load industry with id: " + str(industry_id))
            
            session.delete(db_industry)
        
        return Response(status_code=HTTP_204_NO_CONTENT)
    
    except ValidationError as val_err:
        raise HTTPException(status_code=500, detail=str(val_err))
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))