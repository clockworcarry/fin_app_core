from unicodedata import category
from xmlrpc.client import boolean
from fastapi import APIRouter, status, HTTPException, Response, Header, Depends, Request
from fastapi.security import OAuth2PasswordBearer
from typing import Optional, List
from pydantic import BaseModel, ValidationError, validator

from py_common_utils_gh.os_common_utils import setup_logger, default_log_formatter
from py_common_utils_gh.db_utils.db_utils import SqlAlchemySessionManager
from db.models import *
from sqlalchemy import create_engine, select, insert, exists
from sqlalchemy.orm import sessionmaker

import api.security.security as app_security

import api.shared_models as shared_models
import core.shared_models as shared_models_core
import core.metrics_classifications as metrics_classifications_core


from typing import Union

import api.config as api_config
import api.constants as api_constants
import core.constants as core_global_constants

router = APIRouter(
    prefix="/" + api_constants.app_name + "/" + api_constants.version + "/metrics/categories",
    tags=["metricsCategories"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)

#session = Depends(api_utils.get_db_session), current_user: Account = Depends(app_security.get_current_user
@router.get("", status_code=status.HTTP_200_OK, response_model=List[shared_models_core.MetricCategoryShortModel], summary="Retrieve all metric categories user has access to.",
            description="Only the basic info for the categories will be displayed in this view. To see metrics in the categories, other apis must be used.", response_description="List of metric categories.")
def get_metrics_classifications(request: Request):
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            metric_categories = metrics_classifications_core.get_user_metric_categories(request.state.rctx.user_id, session)
            metric_categories = metrics_classifications_core.group_metric_categories_model(metric_categories, None)
            
            return metric_categories

    except ValidationError as val_err:
        raise HTTPException(status_code=500, detail=str(val_err))
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))