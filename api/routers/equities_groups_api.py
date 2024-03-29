from xmlrpc.client import boolean
from fastapi import APIRouter, status, HTTPException, Request, Response, Depends
from starlette.status import HTTP_204_NO_CONTENT, HTTP_200_OK
from typing import Optional, List
from pydantic import BaseModel, ValidationError, validator

from py_common_utils_gh.os_common_utils import setup_logger, default_log_formatter
from py_common_utils_gh.db_utils.db_utils import SqlAlchemySessionManager

from db.models import *

import api.shared_models as shared_models
import core.shared_models as shared_models_core
import core.metrics_classifications as metrics_classifications_core

import api.config as api_config
import api.constants as api_constants
import core.constants as core_global_constants

router = APIRouter(
    prefix="/" + api_constants.app_name + "/" + api_constants.version + "/" + "equities/groups",
    tags=["equitiesGroups"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)

@router.get("", status_code=HTTP_200_OK, response_model=List[shared_models_core.CompanyGroupInfoShortModel], summary="Get groups for a user.",
            description="Will only return groups user has access to. Will only contain groups' basic info.", response_description="List of groups with their basic info.")
def get_user_groups(request: Request):
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            groups = session.query(CompanyGroup).join(UserCompanyGroup, UserCompanyGroup.group_id == CompanyGroup.id).filter(UserCompanyGroup.account_id == request.state.rctx.user_id).all()
            
            resp = []
            for res in groups:
                resp.append(shared_models_core.CompanyGroupInfoShortModel(id=res.id, name_code=res.name_code, name=res.name))
            
            return resp

    except ValidationError as val_err:
        raise HTTPException(status_code=500, detail=str(val_err))
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))