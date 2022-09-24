import datetime, base64
import numpy as np
from psycopg2 import *

from xmlrpc.client import boolean
from fastapi import APIRouter, status, HTTPException, Request
from typing import Optional, List
from pydantic import BaseModel, ValidationError, validator

from py_common_utils_gh.os_common_utils import setup_logger, default_log_formatter
from py_common_utils_gh.db_utils.db_utils import SqlAlchemySessionManager

from sqlalchemy import create_engine, select, insert, exists
from sqlalchemy.orm import sessionmaker

from db.models import *

import api.routers.company_metric_api as metric_api
import api.routers.shared_models as shared_models

import api.security.security as app_security


import simplejson as json

import api.config as api_config

router = APIRouter(
    prefix="/company/metrics",
    tags=["companyMetrics"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)

class ClassificationModelIn(BaseModel):
    category_name: str
    parent_id: int = None

class CreateClassificationsModelIn(BaseModel):
    classifications = List[ClassificationModelIn]
    account_id: int = None

class MetricsClassificationFine(BaseModel):
    category_name: str
    account_id: int
    classifications: List['MetricsClassificationFine']

class GetGroupMetricsOut(BaseModel):
    group_info: shared_models.CompanyGroupMetricsModelShortOut

# get a group with eveyrthing related to it
# get all metrics for a user
# get all groups user has access to



@router.get("/{bop_id}", response_model=List[metric_api.CompanyMetricApiModelOut])
def get_company_metrics(bop_id, loadDescriptions: Optional[bool] = True, loadDescriptionsNotes: Optional[bool] = False):
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            db_metrics = session.query(CompanyMetric).filter(CompanyMetric.company_business_or_product_id == bop_id).all()
            
            db_metrics_descriptions = []
            if loadDescriptions:
                for metric in db_metrics:
                    db_desc = session.query(CompanyMetricDescription).join(CompanyMetricRelation, CompanyMetricDescription.id == CompanyMetricRelation.company_metric_description_id) \
                                                                     .filter(CompanyMetricRelation.id == metric.company_metric_relation_id).first()
                                                
                    if db_desc is not None:
                        db_metrics_descriptions.append(tuple((metric, db_desc)))

            
            resp = []

            if len(db_metrics_descriptions) > 0:
                for md in db_metrics_descriptions:
                    out_desc = metric_api.CompanyMetricDescriptionApiModelOut(id=md[1].id, code=md[1].code, display_name=md[1].display_name, metric_data_type=md[1].metric_data_type,
                                                                    metric_duration=md[1].metric_duration, metric_duration_type=md[1].metric_duration_type, look_back=md[1].look_back,
                                                                    year_recorded=md[1].year_recorded, quarter_recorded=md[1].quarter_recorded, metric_fixed_year=md[1].metric_fixed_year,
                                                                    metric_fixed_quarter=md[1].metric_fixed_quarter)
                    
                    new_metric = metric_api.CompanyMetricApiModelOut(data=md[0].data, description=out_desc)
                    resp.append(new_metric)
            
            return resp

    except ValidationError as val_err:
        raise HTTPException(status_code=500, detail=str(val_err))
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))



    """get all groups for a user

    Raises:
        HTTPException: Pydantic model validation error
        HTTPException: Generic failure

    Returns:
        List[shared_models.CompanyGroupModelShortOut]: list of all the groups the user has access to
    """
@router.get("/user/groups", response_model=List[shared_models.CompanyGroupModelShortOut])
def get_group_metrics(grp_id, request: Request):
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            rctx = app_security.authenticate_request(request, session)
            db_rows = session.query(UserCompanyGroup, CompanyGroup).join(CompanyGroup, CompanyGroup.id == UserCompanyGroup.group_id) \
                                                                    .filter(UserCompanyGroup.account_id == rctx.user_id).all()

            ret = []
            for dr in db_rows:
                ret.append(shared_models.CompanyGroupModelShortOut(id=dr[1].id, name_code=dr[1].name_code, name=dr[1].name))
            
            return ret

    except ValidationError as val_err:
        raise HTTPException(status_code=500, detail=str(val_err))
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))



    """Get all the metric data for a group

    Raises:
        HTTPException: _description_
        HTTPException: _description_
        HTTPException: _description_

    Returns:
        the metric data for the group
    """
@router.get("/group/{grp_id}", response_model=shared_models.CompanyGroupMetricsModelOut])
def get_group_metrics(grp_id, request: Request):
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            rctx = app_security.authenticate_request(request, session)
            db_rows = session.query(CompanyGroup, CompanyInGroup, CompanyBusinessSegment, CompanyGroupMetricDescription, MetricDescription, MetricData).join(CompanyInGroup, CompanyInGroup.group_id == CompanyGroup.id) \
                                                                                                .join(CompanyGroupMetricDescription, CompanyGroupMetricDescription.company_group_id == CompanyGroup.id) \
                                                                                                .join(MetricDescription, MetricDescription.id == CompanyGroupMetricDescription.metric_description_id) \
                                                                                                .join(MetricData, and_(MetricData.metric_description_id == MetricDescription.id, MetricData.company_business_segment_id == CompanyInGroup.company_business_segment_id)) \
                                                                                                .filter(CompanyGroup.id == grp_id).all()

            ret = shared_models.CompanyGroupMetricsModelOut()
            if len(db_rows) > 0:
                cgms = shared_models.CompanyGroupModelShortOut(id=db_rows[0][0].id, name_code=db_rows[0].name_code, name=db_rows[0].name)
                ret = shared_models.CompanyGroupMetricsModelOut(group_info=cgms)
                for dr in db_rows:
                    ebs = None
                    for bs in ret.business_segments:
                        if bs.id == dr[2].id:
                            ebs = bs
                            break
                    
                    if ebs is None:
                        ret.business_segments.append(shared_models.BusinessSegmentModelOut(id=dr[2].id, company_id=dr[2].company_id, code=dr[2].code, display_name=dr[2].display_name))
                        ebs = ret.business_segments[-1]
                    
                    mdmo = shared_models.MetricDataModelOut(data=dr[5].data)
                    mdmo.description = shared_models.MetricDescriptionModelOut(id=dr[4].id, code=dr[4].code, display_name=dr[4].display_name, metric_data_type=dr[4].metric_data_type, \
                                                                                metric_duration=dr[4].metric_duration, metric_duration_type=dr[4].metric_duration_type, look_back=dr[4].look_back, \
                                                                                year_recorded=dr[4].year_recorded, quarter_recorded=dr[4].quarter_recorded, metric_fixed_year=dr[4].metric_fixed_year, \
                                                                                metric_fixed_quarter = dr[4].metric_fixed_quarter)
                    ebs.metrics.append(mdmo)

            return ret                                             



    except ValidationError as val_err:
        raise HTTPException(status_code=500, detail=str(val_err))
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))