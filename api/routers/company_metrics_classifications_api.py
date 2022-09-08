from unicodedata import category
from xmlrpc.client import boolean
from fastapi import APIRouter, status, HTTPException, Response, Header, Depends, Request
from fastapi.security import OAuth2PasswordBearer
from typing import Optional, List
from pydantic import BaseModel, ValidationError, validator

from py_common_utils_gh.os_common_utils import setup_logger, default_log_formatter
from py_common_utils_gh.db_utils.db_utils import SqlAlchemySessionManager
from db.models import *
import numpy as np
from psycopg2 import *
from sqlalchemy import create_engine, select, insert, exists
from sqlalchemy.orm import sessionmaker

import api.security.security as app_security

import api.routers.company_metric_api as metric_api
import core.company_metrics_classifications as metrics_classifications_core

import datetime, base64

from typing import Union

import simplejson as json

import api.config as api_config
import api.utils.utils as api_utils

router = APIRouter(
    prefix="/metricsClassifications",
    tags=["metricsClassifications"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)

class ClassificationModelIn(BaseModel):
    category_name: str
    parent_id: int = None

class CreateClassificationsModelIn(BaseModel):
    classifications: List[ClassificationModelIn]
    creator_id: int = None

class OutputClassificationsModelOut(BaseModel):
    classifications: List['MetricsClassificationFineOut'] = []

class MetricsClassificationFineOut(BaseModel):
    id: int
    category_name: str
    parent_id: int = None
    classifications: List['MetricsClassificationFineOut'] = []

MetricsClassificationFineOut.update_forward_refs()

manager = SqlAlchemySessionManager()

def metrics_classification_to_pydantic_model(cls):
    elem = MetricsClassificationFineOut(id=cls.id, category_name=cls.category_name, parent_id=cls.parent_id)
    for c in cls.classifications:
        elem.classifications.append(metrics_classification_to_pydantic_model(c))
        metrics_classification_to_pydantic_model(c)
    
    return elem

def metrics_classifications_to_pydantic_model(grouped_classifications):
    ret = []
    for gc in grouped_classifications:
        ret.append(metrics_classification_to_pydantic_model(gc))
    
    return ret

#session = Depends(api_utils.get_db_session), current_user: Account = Depends(app_security.get_current_user
@router.get("/", status_code=status.HTTP_200_OK)
def get_metrics_classifications_no_id(request: Request):
    try:
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            rctx = app_security.authenticate_request(request, session)
            grouped_classifications = metrics_classifications_core.get_metrics_classifications_by_account(rctx.user_id, session)
            ret = OutputClassificationsModelOut(account_id=None)
            ret.classifications = metrics_classifications_to_pydantic_model(grouped_classifications)
            
            return ret

    except ValidationError as val_err:
        raise HTTPException(status_code=500, detail=str(val_err))
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))

@router.get("/{search_id}", status_code=status.HTTP_200_OK, response_model=OutputClassificationsModelOut)
def get_metrics_classifications(search_id, request: Request):
    try:
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            app_security.authenticate_request(request, session)
            grouped_classifications = metrics_classifications_core.get_metrics_classifications_by_creator(search_id, session)
            ret = OutputClassificationsModelOut()
            ret.classifications = metrics_classifications_to_pydantic_model(grouped_classifications)
        
            return ret


    except ValidationError as val_err:
        raise HTTPException(status_code=500, detail=str(val_err))
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_metrics_classifications(body: CreateClassificationsModelIn):
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            db_classifications = session.query(CompanyMetricClassificationAccountRelation, CompanyMetricClassification) \
                                .join(CompanyMetricClassification, CompanyMetricClassification.id == CompanyMetricClassificationAccountRelation.company_metric_classification_id) \
                                .filter(or_(CompanyMetricClassificationAccountRelation.account_id == body.account_id, CompanyMetricClassificationAccountRelation.account_id == None)).all()
            for c in body.classifications:
                for db_c in db_classifications:
                    if c.category_name == db_c[1].category_name:
                        raise Exception("A classification with name: " + c.category_name + " already exists for this user.")
                
                new_class = CompanyMetricClassification(category_name=c.category_name, parent_category_id=c.parent_id)
                session.add(new_class)
                session.flush()
                session.add(CompanyMetricClassificationAccountRelation(company_metric_classification_id=new_class.id, account_id=body.account_id))         

    except ValidationError as val_err:
        raise HTTPException(status_code=500, detail=str(val_err))
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))

@router.put("/{classification_id}")
def update_metrics_classification(classification_id, body: ClassificationModelIn):
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            db_classification = session.query(CompanyMetricClassification).filter(CompanyMetricClassification.id == classification_id).first()
            if db_classification is None:
                raise Exception("No classification with id: " + str(classification_id) + " exists.")
            db_classification.category_name = body.category_name
            db_classification.parent_category_id = body.parent_id

        return Response(status_code=status.HTTP_204_NO_CONTENT)

    except ValidationError as val_err:
        raise HTTPException(status_code=500, detail=str(val_err))
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))

@router.delete("/{classification_id}")
def delete_metrics_classification(classification_id):
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            db_classification = session.query(CompanyMetricClassification).filter(CompanyMetricClassification.id == classification_id).first()
            if db_classification is None:
                raise Exception("No classification with id: " + str(classification_id) + " exists.")
            session.delete(db_classification)

        return Response(status_code=status.HTTP_204_NO_CONTENT)

    except ValidationError as val_err:
        raise HTTPException(status_code=500, detail=str(val_err))
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))