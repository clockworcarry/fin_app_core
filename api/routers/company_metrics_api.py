from xmlrpc.client import boolean
from fastapi import APIRouter, status, HTTPException
from typing import Optional, List
from pydantic import BaseModel, ValidationError, validator

from py_common_utils_gh.os_common_utils import setup_logger, default_log_formatter
from py_common_utils_gh.db_utils.db_utils import SqlAlchemySessionManager
from db.models import *
import numpy as np
from psycopg2 import *
from sqlalchemy import create_engine, select, insert, exists
from sqlalchemy.orm import sessionmaker

import api.routers.company_metric_api as metric_api

import datetime, base64

import simplejson as json

import api.config as api_config

router = APIRouter(
    prefix="/company/metrics",
    tags=["companyMetrics"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)

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

@router.get("/group/{grp_id}", response_model=List[metric_api.CompanyMetricApiModelOut])
def get_company_metrics(grp_id, loadDescriptions: Optional[bool] = True, loadDescriptionsNotes: Optional[bool] = False):
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            db_rows = session.query(CompanyGroupRelation, CompanyMetric).join(CompanyBusinessOrProduct, CompanyBusinessOrProduct.id == CompanyGroupRelation.company_business_or_product_id) \
                                                                        .join(CompanyMetric, CompanyMetric.company_business_or_product_id == CompanyBusinessOrProduct.id) \
                                                                        .filter(CompanyGroupRelation.group_id == grp_id).all()
            if len(db_rows) == 0:
                raise HTTPException(status_code=500, detail="Failed to load metrics for this group.")


            
            db_metrics_descriptions = []
            if loadDescriptions:
                for row in db_rows:
                    metric_obj = row[1]
                    db_desc = session.query(CompanyMetricDescription).join(CompanyMetricRelation, CompanyMetricDescription.id == CompanyMetricRelation.company_metric_description_id) \
                                                                     .filter(CompanyMetricRelation.id == metric_obj.company_metric_relation_id).first()
                                                
                    if db_desc is not None:
                        db_metrics_descriptions.append(tuple((metric_obj, db_desc)))

            
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