from fastapi import APIRouter, status, HTTPException
from typing import Optional, List
from pydantic import BaseModel, ValidationError, validator

from py_common_utils_gh.os_common_utils import setup_logger, default_log_formatter
from py_common_utils_gh.db_utils.db_utils import SqlAlchemySessionManager
from db.models import *
from db.company_financials import *
import numpy as np
from psycopg2 import *
from sqlalchemy import create_engine, select, insert, exists
from sqlalchemy.orm import sessionmaker

import datetime, base64

import simplejson as json

import api.config as api_config

router = APIRouter(
    prefix="/company/financials",
    tags=["companyFinancials"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)

class CompanyFinancialsApiModelIn(BaseModel):
    effective_tax_rate: float
    calendar_date: datetime.date

@router.post("/{company_id}", response_model=CompanyMetricDescriptionApiModelOut)
def update_financials(company_id, body: CompanyFinancialsApiModelIn):
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            db_financials = session.query(CompanyFinancialData).filter(CompanyFinancialData.calendar_date == body.calendar_date).first()
            if db_financials is None:
                raise HTTPException(status_code=500, detail="No financial report with date: " + str(calendar_date) + " exists.")
            
            if body.effective_tax_rate.code is not None:
                db_metric_desc.code = metric_description.code
            if metric_description.display_name is not None:
                db_metric_desc.display_name = metric_description.display_name
            if metric_description.metric_data_type is not None:
                db_metric_desc.metric_data_type = metric_description.metric_data_type

            session.flush()
            ret = CompanyMetricDescriptionApiModelOut(id=db_metric_desc.id, code=db_metric_desc.code, display_name=db_metric_desc.display_name, metric_data_type=db_metric_desc.metric_data_type)
            return ret
    except ValidationError as val_err:
        raise HTTPException(status_code=500, detail=str(val_err))
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))

@router.get("/{company_id}", response_model=CompanyMetricDescriptionApiModelOut)
