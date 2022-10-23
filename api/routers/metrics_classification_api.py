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
    prefix="/" + api_constants.app_name + "/" + api_constants.version + "/metrics/category",
    tags=["metricsCategory"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)

class MetricClassificationModelIn(BaseModel):
    id: int = 0
    category_name: str
    parent_id: Union[int, None]

@router.post("", status_code=status.HTTP_201_CREATED)
def create_metrics_classification(request: Request, body: MetricClassificationModelIn):
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            db_classifications = session.query(MetricClassification, UserMetricClassification) \
                                        .join(UserMetricClassification, UserMetricClassification.metric_classification_id == MetricClassification.id) \
                                        .filter(or_(UserMetricClassification.account_id == core_global_constants.system_user_id, UserMetricClassification.account_id == request.state.rctx.user_id)) \
                                        .all()

            parent_exists = False
            for mc, umc in db_classifications:
                if body.category_name == mc.category_name:
                    raise Exception("A category with name: " + body.category_name + " already exists for this user.")
                if body.parent_id == mc.id:
                    parent_exists = True

            if not parent_exists and body.parent_id is not None:
                raise Exception("Parent id " + str(body.parent_id) + " could not be associated to any existing categories.")
                
            new_class = MetricClassification(category_name=body.category_name, parent_category_id=body.parent_id, creator_id=request.state.rctx.user_id)
            session.add(new_class)
            session.flush()
            session.add(UserMetricClassification(metric_classification_id=new_class.id, account_id=request.state.rctx.user_id))         

    except ValidationError as val_err:
        raise HTTPException(status_code=500, detail=str(val_err))
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))

@router.put("/{classification_id}", status_code=status.HTTP_204_NO_CONTENT)
def update_metrics_classification(classification_id, request: Request, body: MetricClassificationModelIn):
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            db_classifications = session.query(MetricClassification, UserMetricClassification) \
                                        .join(UserMetricClassification, UserMetricClassification.metric_classification_id == MetricClassification.id) \
                                        .filter(or_(UserMetricClassification.account_id == core_global_constants.system_user_id, UserMetricClassification.account_id == request.state.rctx.user_id)) \
                                        .all()

            selected_classification = None
            parent_exists = False
            for mc, umc in db_classifications:
                if body.category_name == mc.category_name:
                    raise Exception("A category with name: " + body.category_name + " already exists for this user.")
                if body.parent_id == mc.id:
                    parent_exists = True
                    if mc.parent_category_id == int(classification_id):
                         raise Exception("Cannot set parent to a category whose parent is this category. Circular dependency.")
                if mc.id == int(classification_id):
                    selected_classification = mc

            if not parent_exists and body.parent_id is not None:
                raise Exception("Parent id " + str(body.parent_id) + " could not be associated to any existing categories.")
            
            if selected_classification is None:
                raise Exception("Failed to load a metric category with id: " + classification_id)

            selected_classification.category_name = body.category_name
            selected_classification.parent_category_id = body.parent_id

        return Response(status_code=status.HTTP_204_NO_CONTENT)

    except ValidationError as val_err:
        raise HTTPException(status_code=500, detail=str(val_err))
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))

@router.delete("/{classification_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_metrics_classification(classification_id):
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            db_classifications = session.query(MetricClassification).all()
            
            selected_classification = None
            for cls in db_classifications:
                if cls.id == int(classification_id):
                    selected_classification = cls
            
            if selected_classification is None:
                raise Exception("Failed to load a metric category with id: " + classification_id)
            
            for cls in db_classifications:
                if cls.parent_category_id == selected_classification.id:
                    cls.parent_category_id = None

            
            session.delete(selected_classification)

        return Response(status_code=status.HTTP_204_NO_CONTENT)

    except ValidationError as val_err:
        raise HTTPException(status_code=500, detail=str(val_err))
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))