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
import core.shared_models as shared_models_core
import core.metrics_classifications as metrics_classifications_core

import api.constants as api_constants

import api.security.security as app_security


import simplejson as json

import api.config as api_config

import copy

router = APIRouter(
    prefix="/" + api_constants.app_name + "/" + api_constants.version + "/" + "equities/group",
    tags=["equitiesGroup"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)

"""Get all the metric data for a group
   /equities/group/metrics/{grp_id}

Raises:
    HTTPException: _description_
    HTTPException: _description_
    HTTPException: _description_

Returns:
    the metric data for the group
"""
@router.get("/metrics/{grp_id}", response_model=shared_models_core.CompanyGroupMetricsModel)
def get_group_metrics(grp_id, request: Request):
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            rctx = app_security.authenticate_request(request, session)
            
            metric_categories = metrics_classifications_core.get_user_metric_categories(rctx.user_id, session)

            db_rows = session.query(CompanyGroup, CompanyInGroup, CompanyGroupMetricDescription, MetricDescription, MetricData, CompanyBusinessSegment, Company) \
                                                                                                .join(CompanyInGroup, CompanyInGroup.group_id == CompanyGroup.id) \
                                                                                                .join(CompanyGroupMetricDescription, CompanyGroupMetricDescription.company_group_id == CompanyGroup.id) \
                                                                                                .join(MetricDescription, MetricDescription.id == CompanyGroupMetricDescription.metric_description_id) \
                                                                                                .join(MetricData, and_(MetricData.metric_description_id == MetricDescription.id, MetricData.company_business_segment_id == CompanyInGroup.company_business_segment_id)) \
                                                                                                .join(CompanyBusinessSegment, CompanyBusinessSegment.id == MetricData.company_business_segment_id) \
                                                                                                .join(Company, Company.id == CompanyBusinessSegment.company_id) \
                                                                                                .filter(CompanyGroup.id == grp_id).all()
            

            if len(db_rows) == 0:
                raise Exception("No data found for group_id: " + str(grp_id))

            business_segments = []

            #initialize business segments
            for row in db_rows:
                row_business_segment = row[5]
                row_company = row[6]
                ebs = None
                for bs in business_segments:
                    if bs.id == row_business_segment.id:
                        ebs = bs
                        break
                
                if ebs is None:
                    business_segments.append(shared_models_core.BusinessSegmentModel(id=row_business_segment.id, code=row_business_segment.code, display_name=row_business_segment.display_name, \
                                                                                     company_id=row_business_segment.company_id, company_name=row_company.name, company_ticker=row_company.ticker))
                    ebs = business_segments[-1]
                    ebs.metric_categories = copy.deepcopy(metric_categories)
            
            #add metrics to proper categories in the proper business segment
            for row in db_rows:
                row_metric_description = row[3]
                row_metric_data = row[4]
                row_business_segment = row[5]
                metric_desc_model = shared_models_core.MetricDescriptionModel.from_orm(row_metric_description)
                metric_data = shared_models_core.MetricDataModel(data=row_metric_data.data, description=metric_desc_model)
                
                ebs = None
                for bs in business_segments:
                    if bs.id == row_business_segment.id:
                        ebs = bs
                        break
                
                if ebs is not None:
                    for cat in ebs.metric_categories:
                        if cat.id == row_metric_description.metric_classification_id:
                            cat.metrics.append(metric_data)
                            break
            
            #group categories in business segment (tree hierarchy, categories can be nested recursively)
            for bs in business_segments:
                bs.metric_categories = metrics_classifications_core.group_metric_categories_model(bs.metric_categories, None)
                #remove categories with no metrics or sub categories
                metrics_classifications_core.remove_empty_categories(bs.metric_categories)

            group_info = shared_models_core.CompanyGroupInfoShortModel(id=db_rows[0][0].id, name_code=db_rows[0][0].name_code, name=db_rows[0][0].name)

            ret = shared_models_core.CompanyGroupMetricsModel(group_info=group_info, business_segments=business_segments)

            print(shared_models_core.CompanyGroupMetricsModel.parse_obj(ret).json()) 

            return ret                                      


    except ValidationError as val_err:
        raise HTTPException(status_code=500, detail=str(val_err))
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))