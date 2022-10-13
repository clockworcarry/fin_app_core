

from fastapi import APIRouter, status, HTTPException, Request, Response
from starlette.status import HTTP_204_NO_CONTENT
from typing import Optional, List
from pydantic import BaseModel, ValidationError, validator

from py_common_utils_gh.os_common_utils import setup_logger, default_log_formatter
from py_common_utils_gh.db_utils.db_utils import SqlAlchemySessionManager

from sqlalchemy import create_engine, select, insert, exists
from sqlalchemy.orm import sessionmaker

from db.models import *

import core.shared_models as shared_models_core
import core.metrics_classifications as metrics_classifications_core

import api.constants as api_constants

import api.security.security as app_security


import simplejson as json

import api.config as api_config

router = APIRouter(
    prefix="/" + api_constants.app_name + "/" + api_constants.version + "/" + "equities/user",
    tags=["equitiesUser"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)

    """returns a list of group_ids for all the groups the user has access to

    Raises:
        HTTPException: _description_
        HTTPException: _description_
        HTTPException: _description_
        HTTPException: _description_
        HTTPException: _description_
        HTTPException: _description_
        HTTPException: _description_
        HTTPException: _description_
        HTTPException: _description_
        HTTPException: _description_
        HTTPException: _description_
        HTTPException: _description_
        HTTPException: _description_
        HTTPException: _description_
        HTTPException: _description_
        HTTPException: _description_

    Returns:
        _type_: _description_
    """
@router.get("/groups", status_code=HTTP_204_NO_CONTENT)
def get_user_groups(grp_id, desc_id, request: Request):
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            db_grp = session.query(CompanyGroup).filter(CompanyGroup.id == grp_id).first()
            if db_grp is None:
                raise HTTPException(status_code=500, detail="No group with id: " + str(grp_id) + " exists.")
            
            db_metric_desc = session.query(MetricDescription).filter(MetricDescription.id == desc_id).first()
            if db_metric_desc is None:
                raise HTTPException(status_code=500, detail="No metric description with id: " + str(desc_id) + " exists.")
            
            session.add(CompanyGroupMetricDescription(metric_description_id=desc_id, company_group_id=grp_id))

            return Response(status_code=HTTP_204_NO_CONTENT)

    except ValidationError as val_err:
        raise HTTPException(status_code=500, detail=str(val_err))
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))


    """Return all metric descriptions that the user has access to

    Raises:
        HTTPException: _description_
        HTTPException: _description_
        HTTPException: _description_
        HTTPException: _description_
        HTTPException: _description_
        HTTPException: _description_
        HTTPException: _description_
        HTTPException: _description_
        HTTPException: _description_
        HTTPException: _description_
        HTTPException: _description_
        HTTPException: _description_

    Returns:
        _type_: _description_
    """
@router.get("/metricDescriptions", status_code=HTTP_204_NO_CONTENT)
def get_user_metric_descriptions(grp_id, desc_id, request: Request):
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            db_grp = session.query(CompanyGroup).filter(CompanyGroup.id == grp_id).first()
            if db_grp is None:
                raise HTTPException(status_code=500, detail="No group with id: " + str(grp_id) + " exists.")
            
            db_metric_desc = session.query(MetricDescription).filter(MetricDescription.id == desc_id).first()
            if db_metric_desc is None:
                raise HTTPException(status_code=500, detail="No metric description with id: " + str(desc_id) + " exists.")
            
            session.add(CompanyGroupMetricDescription(metric_description_id=desc_id, company_group_id=grp_id))

            return Response(status_code=HTTP_204_NO_CONTENT)

    except ValidationError as val_err:
        raise HTTPException(status_code=500, detail=str(val_err))
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))

    """Returns all the metric descriptions from a specific toolbox. A subset of all the metrics.

    Raises:
        HTTPException: _description_
        HTTPException: _description_
        HTTPException: _description_
        HTTPException: _description_
        HTTPException: _description_
        HTTPException: _description_
        HTTPException: _description_
        HTTPException: _description_
        HTTPException: _description_
        HTTPException: _description_
        HTTPException: _description_
        HTTPException: _description_
        HTTPException: _description_
        HTTPException: _description_
        HTTPException: _description_
        HTTPException: _description_

    Returns:
        _type_: _description_
    """
@router.get("/metricDescriptions/{toolbox_id}", status_code=HTTP_204_NO_CONTENT)
def get_user_metric_descriptions_toolbox(grp_id, desc_id, request: Request):
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            db_grp = session.query(CompanyGroup).filter(CompanyGroup.id == grp_id).first()
            if db_grp is None:
                raise HTTPException(status_code=500, detail="No group with id: " + str(grp_id) + " exists.")
            
            db_metric_desc = session.query(MetricDescription).filter(MetricDescription.id == desc_id).first()
            if db_metric_desc is None:
                raise HTTPException(status_code=500, detail="No metric description with id: " + str(desc_id) + " exists.")
            
            session.add(CompanyGroupMetricDescription(metric_description_id=desc_id, company_group_id=grp_id))

            return Response(status_code=HTTP_204_NO_CONTENT)

    except ValidationError as val_err:
        raise HTTPException(status_code=500, detail=str(val_err))
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))


    """Returns the data for a metric description. It is either the one from the sysetm (shared one) or the user-overriden one

    Raises:
        HTTPException: _description_
        HTTPException: _description_
        HTTPException: _description_
        HTTPException: _description_
        HTTPException: _description_
        HTTPException: _description_
        HTTPException: _description_
        HTTPException: _description_
        HTTPException: _description_
        HTTPException: _description_
        HTTPException: _description_
        HTTPException: _description_

    Returns:
        _type_: _description_
    """
@router.get("/metricData/{metric_desc_id}/{bs_id}", status_code=HTTP_204_NO_CONTENT)
def get_user_metric_data(grp_id, desc_id, request: Request):
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            db_grp = session.query(CompanyGroup).filter(CompanyGroup.id == grp_id).first()
            if db_grp is None:
                raise HTTPException(status_code=500, detail="No group with id: " + str(grp_id) + " exists.")
            
            db_metric_desc = session.query(MetricDescription).filter(MetricDescription.id == desc_id).first()
            if db_metric_desc is None:
                raise HTTPException(status_code=500, detail="No metric description with id: " + str(desc_id) + " exists.")
            
            session.add(CompanyGroupMetricDescription(metric_description_id=desc_id, company_group_id=grp_id))

            return Response(status_code=HTTP_204_NO_CONTENT)

    except ValidationError as val_err:
        raise HTTPException(status_code=500, detail=str(val_err))
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))


@router.get("/companies/watchlist", status_code=HTTP_204_NO_CONTENT)
def add_metric_description_to_group(grp_id, desc_id, request: Request):
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            db_grp = session.query(CompanyGroup).filter(CompanyGroup.id == grp_id).first()
            if db_grp is None:
                raise HTTPException(status_code=500, detail="No group with id: " + str(grp_id) + " exists.")
            
            db_metric_desc = session.query(MetricDescription).filter(MetricDescription.id == desc_id).first()
            if db_metric_desc is None:
                raise HTTPException(status_code=500, detail="No metric description with id: " + str(desc_id) + " exists.")
            
            session.add(CompanyGroupMetricDescription(metric_description_id=desc_id, company_group_id=grp_id))

            return Response(status_code=HTTP_204_NO_CONTENT)

    except ValidationError as val_err:
        raise HTTPException(status_code=500, detail=str(val_err))
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))


@router.get("/companies/watchlist", status_code=HTTP_204_NO_CONTENT)
def add_metric_description_to_group(grp_id, desc_id, request: Request):
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            db_grp = session.query(CompanyGroup).filter(CompanyGroup.id == grp_id).first()
            if db_grp is None:
                raise HTTPException(status_code=500, detail="No group with id: " + str(grp_id) + " exists.")
            
            db_metric_desc = session.query(MetricDescription).filter(MetricDescription.id == desc_id).first()
            if db_metric_desc is None:
                raise HTTPException(status_code=500, detail="No metric description with id: " + str(desc_id) + " exists.")
            
            session.add(CompanyGroupMetricDescription(metric_description_id=desc_id, company_group_id=grp_id))

            return Response(status_code=HTTP_204_NO_CONTENT)

    except ValidationError as val_err:
        raise HTTPException(status_code=500, detail=str(val_err))
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))