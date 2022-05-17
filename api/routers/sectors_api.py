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
    prefix="/sectors",
    tags=["sectors"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)

class SectorsApiModelOut(BaseModel):
    id: int
    name: str
    name_code: str
    locked: bool

@router.get("", response_model=List[SectorsApiModelOut])
def get_all_sectors():
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            query_res = session.query(Sector).all()
            
            resp = []
            
            for res in query_res:
                resp.append(SectorsApiModelOut(id=res.id, name=res.name, name_code=res.name_code, locked=res.locked))
            
            return resp

    except ValidationError as val_err:
        raise HTTPException(status_code=500, detail=str(val_err))
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))