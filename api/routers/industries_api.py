from fastapi import APIRouter, status, HTTPException
from typing import Optional, List
from pydantic import BaseModel, ValidationError, validator

from py_common_utils_gh.os_common_utils import setup_logger, default_log_formatter
from py_common_utils_gh.db_utils.db_utils import SqlAlchemySessionManager
from db.models import *

import api.config as api_config
import api.constants as api_constants
import core.constants as core_constants

router = APIRouter(
    prefix="/" + api_constants.app_name + "/" + api_constants.version + "/industries",
    tags=["industries"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)

class IndustryModelOut(BaseModel):
    id: int
    sector_id: int
    name: str
    name_code: str

@router.get("/", response_model=List[IndustryModelOut])
def get_all_industries():
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            industries = session.query(Industry).all()
            
            resp = []
            for res in industries:
                resp.append(IndustryModelOut(id=res.id, sector_id=res.sector_id, name=res.name, name_code=res.name_code))
            
            return resp

    except ValidationError as val_err:
        raise HTTPException(status_code=500, detail=str(val_err))
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))

@router.get("/{sector_id}", response_model=List[IndustryModelOut])
def get_all_sector_industries(sector_id):
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            industries = session.query(Industry).filter(Industry.sector_id == sector_id).all()
            
            resp = []         
            for res in industries:
                resp.append(IndustryModelOut(id=res.id, sector_id=res.sector_id, name=res.name, name_code=res.name_code))
            
            return resp

    except ValidationError as val_err:
        raise HTTPException(status_code=500, detail=str(val_err))
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))