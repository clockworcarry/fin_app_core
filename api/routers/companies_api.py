from fastapi import APIRouter, status, HTTPException, File, UploadFile, Query, Response
from typing import Optional, List, Union
from pydantic import BaseModel, ValidationError, validator
from starlette.status import HTTP_204_NO_CONTENT, HTTP_201_CREATED, HTTP_200_OK, HTTP_501_NOT_IMPLEMENTED

from py_common_utils_gh.os_common_utils import setup_logger, default_log_formatter
from py_common_utils_gh.db_utils.db_utils import SqlAlchemySessionManager
from db.models import *

import core.shared_models as shared_models_core

import api.config as api_config
import api.constants as api_constants
import core.constants as core_global_constants

router = APIRouter(
    prefix="/" + api_constants.app_name + "/" + api_constants.version + "/companies",
    tags=["companies"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)


@router.get("/", status_code=status.HTTP_200_OK, response_model=List[shared_models_core.CompanyModel])
def get_companies(search_key, sector_id: Union[int, None]=None, industry_id: Union[int, None]=None):
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            #a company can have multiple business segmetns in different industries. This api should return the company
            #+all the segments that match the query str params
            #db_companies = session.query(Company).filter(Company.)
            pass

    except ValidationError as val_err:
        raise HTTPException(status_code=500, detail=str(val_err))
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))

@router.get("/watchList/{watchlist_id}", status_code=status.HTTP_200_OK, response_model=List[shared_models_core.CompanyModel])
def get_companies(watchlist_id):
    return Response(content="Not implemented", status_code=HTTP_501_NOT_IMPLEMENTED)