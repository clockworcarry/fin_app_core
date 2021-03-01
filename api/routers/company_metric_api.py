from fastapi import APIRouter
from typing import Optional, List
from pydantic import BaseModel, ValidationError, validator

from py_common_utils_gh.os_common_utils import setup_logger, default_log_formatter
from py_common_utils_gh.db_utils.db_utils import SqlAlchemySessionManager
from db.models import *
import numpy as np
from psycopg2 import *
from sqlalchemy import create_engine, select, insert, exists
from sqlalchemy.orm import sessionmaker

import datetime

import simplejson as json

import config

router = APIRouter(
    prefix="/companyMetrics",
    tags=["companyMetrics"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)

class CompanyMetricDescriptionNoteApiModel(BaseModel):
    data: bytes = None
    note_type: int = None

class CompanyMetricApiModel(BaseModel):
    code: str
    display_name: str
    metric_data_type: int
    notes: List[CompanyMetricDescriptionNoteApiModel] = []
    data: float
    date_recorded: datetime.date
    look_back: int

    class Config:
        validate_assignment = True

    @validator('code')
    def code_must_not_be_empty(cls, code):
        if code == None or code == '':
            raise ValueError('Code must not be empty.')
        return code


@router.get("/{company_id}")
def get_company_metrics(company_id, loadDescriptions: Optional[bool] = True, loadDescriptionsNotes: Optional[bool] = True):
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=config.global_api_config.db_conn_str, template_name='default_session') as session:
            query_res = session.query(CompanyMetric, CompanyMetricDescription, CompanyMetricDescriptionNote) \
                                                    .join(CompanyMetricDescription, CompanyMetric.company_metric_description_id == CompanyMetricDescription.id) \
                                                    .outerjoin(CompanyMetricDescriptionNote, CompanyMetricDescriptionNote.company_metric_description_id == CompanyMetricDescription.id) \
                                                    .filter(CompanyMetric.company_id == company_id).order_by(CompanyMetric.date_recorded.desc()).all()

            
            resp = []
            
            for res in query_res:
                new_metric = CompanyMetricApiModel(code=res[1].code, display_name=res[1].display_name, metric_data_type=res[1].metric_data_type, \
                                                   data=res[0].data, date_recorded=res[0].date_recorded, look_back=res[0].look_back)
                for note in res[1].notes:
                    note_model = CompanyMetricDescriptionNoteApiModel()
                    note_model.data = note.note_data
                    note_model.note_type = note.note_type
                    new_metric.notes.append(note_model)
                
                resp.append(new_metric)
            
            return resp

    except ValidationError as val_err:
        return val_err.json()
    except Exception as gen_ex:
        return {"errMsg": str(gen_ex)}