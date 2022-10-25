from urllib.request import Request
from fastapi import APIRouter, status, HTTPException, Response, Request
from typing import Optional, List
from pydantic import BaseModel, ValidationError, validator
from starlette.status import HTTP_204_NO_CONTENT, HTTP_201_CREATED, HTTP_401_UNAUTHORIZED
from fastapi.responses import JSONResponse

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
import api.shared_models as api_shared_models

router = APIRouter(
    prefix="/" + api_constants.app_name + "/" + api_constants.version + "/sector",
    tags=["sector"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)

class SectorSaveModelIn(BaseModel):
    name: str
    name_code: str


@router.post("", status_code=status.HTTP_201_CREATED, response_model=api_shared_models.ResourceCreationBasicModel, summary="Create a new sector.",
            description="This endpoint is only available to system user. Regular users should create groups instead.", response_description="The id of the created sector.")
def create_sector(body: SectorSaveModelIn, request: Request):
    try:
        if request.state.rctx.user_id != core_constants.system_user_id:
            return JSONResponse(status_code=HTTP_401_UNAUTHORIZED, content={'details': "Only system user can create a sector. Other users should create company groups."})
        
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            new_sector = Sector(name=body.name, name_code=body.name_code)
            session.add(new_sector)
            
        return Response(status_code=HTTP_201_CREATED)
    
    except ValidationError as val_err:
        raise HTTPException(status_code=500, detail=str(val_err))
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))

@router.put("/{sector_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Update a sector's info.")
def update_sector(sector_id, body: SectorSaveModelIn, request: Request):
    try:
        if request.state.rctx.user_id != core_constants.system_user_id:
            return JSONResponse(status_code=HTTP_401_UNAUTHORIZED, content={'details': "Only system user can update a sector. Other users should create company groups."})
        
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            db_sector = session.query(Sector).filter(Sector.id == sector_id).first()
            if db_sector is None:
                raise Exception("Could not load sector with id: " + str(sector_id))
            db_sector.name = body.name
            db_sector.name_code = body.name_code
            
        return Response(status_code=HTTP_204_NO_CONTENT)
    
    except ValidationError as val_err:
        raise HTTPException(status_code=500, detail=str(val_err))
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))

@router.delete("/{sector_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a sector.", description="Will also delete dependant entities. See erd for reference.")
def delete_sector(sector_id, request: Request):
    try:
        if request.state.rctx.user_id != core_constants.system_user_id:
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Only system user can delete a sector.")

        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            db_sector = session.query(Sector).filter(Sector.id == sector_id).first()
            if db_sector is None:
                raise Exception("Could not load sector with id: " + str(sector_id))
            
            session.delete(db_sector)
        
        return Response(status_code=HTTP_204_NO_CONTENT)
    
    except ValidationError as val_err:
        raise HTTPException(status_code=500, detail=str(val_err))
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))