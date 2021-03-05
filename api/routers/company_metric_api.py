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

import datetime, base64

import simplejson as json

import api.config as api_config

router = APIRouter(
    prefix="/companyMetric",
    tags=["companyMetric"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)

class CompanyMetricDescriptionNoteApiModelOut(BaseModel):
    data: bytes = None
    note_type: int = None

'''class CompanyMetricApiModelOut(BaseModel):
    code: str
    display_name: str
    metric_data_type: int
    notes: List[CompanyMetricDescriptionNoteApiModelOut] = []
    data: float
    date_recorded: datetime.date
    look_back: int

    class Config:
        validate_assignment = True

    @validator('code')
    def code_must_not_be_empty(cls, code):
        if code == None or code == '':
            raise ValueError('Code must not be empty.')
        return code'''

class CompanyMetricApiModelIn(BaseModel):
    data: float
    look_back: int
    date_recorded: datetime.date

class CompanyMetricApiModelOut(BaseModel):
    id: int
    data: float
    look_back: int
    date_recorded: datetime.date

class CompanyMetricDescriptionApiModelIn(BaseModel):
    code: str
    display_name: str
    metric_data_type: int

class CompanyMetricDescriptionApiModelOut(BaseModel):
    id: int
    code: str
    display_name: str
    metric_data_type: int

class CompanyMetricDescriptionApiModelUpdateIn(BaseModel):
    code: str = None
    display_name: str = None
    metric_data_type: int = None

class CompanyMetricDescriptionNoteApiModelIn(BaseModel):
    data: str
    note_type: int
    company_ids: List[int] = None #list of companies this note applies to. if None, applies to all companies

class CompanyMetricDescriptionNoteApiModelOut(BaseModel):
    metric_description_id: int
    note_id: int
    data: str
    note_type: int
    company_ids: List[int] = None

'''class CompanyMetricDescriptionNoteApiModelOut(BaseModel):
    data: str
    note_type: int
    company_ids: List[int] = None #list of companies this note applies to. if None, applies to all companies'''


'''@router.get("/{company_id}")
def get_company_metrics(company_id, loadDescriptions: Optional[bool] = True, loadDescriptionsNotes: Optional[bool] = True):
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=config.global_api_config.db_conn_str, template_name='default_session') as session:
            query_res = session.query(CompanyMetric, CompanyMetricDescription, CompanyMetricDescriptionNote), \
                                .join(CompanyMetricRelation, or_(CompanyMetricRelation.company_id == CompanyMetric.company_id, CompanyMetricRelation.company_id == None)) \
                                .join(CompanyMetricDescription, CompanyMetricDescription.id == CompanyMetricRelation.company_metric_description_id) \
                                .outerjoin(CompanyMetricDescriptionNote, CompanyMetricDescriptionNote.company_metric_description_id == CompanyMetricDescription.id) \
                                .filter(CompanyMetric.company_id == company_id).order_by(CompanyMetric.date_recorded.desc()).all()

            
            resp = []
            
            for res in query_res:
                new_metric = CompanyMetricApiModelOut(code=res[1].code, display_name=res[1].display_name, metric_data_type=res[1].metric_data_type, \
                                                   data=res[0].data, date_recorded=res[0].date_recorded, look_back=res[0].look_back)
                for note in res[1].notes:
                    note_model = CompanyMetricDescriptionNoteApiModel()
                    note_model.data = note.note_data
                    note_model.note_type = note.note_type
                    new_metric.notes.append(note_model)
                
                resp.append(new_metric)
            
            return resp

    except ValidationError as val_err:
        raise HTTPException(status_code=500, detail=str(gen_ex))
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))'''

@router.post("/description", status_code=status.HTTP_201_CREATED, response_model=CompanyMetricDescriptionApiModelOut)
def save_company_metric_description(metric_description: CompanyMetricDescriptionApiModelIn):
    db_metric_desc = None
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            db_metric_desc = CompanyMetricDescription(code=metric_description.code, display_name=metric_description.display_name, metric_data_type=metric_description.metric_data_type)
            session.add(db_metric_desc)
            session.flush()
            ret = CompanyMetricDescriptionApiModelOut(id=db_metric_desc.id, code=db_metric_desc.code, display_name=db_metric_desc.display_name, metric_data_type=db_metric_desc.metric_data_type)
            return ret

    except ValidationError as val_err:
        raise HTTPException(status_code=500, detail=str(val_err))
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))

@router.post("/description/{description_id}")
def update_company_metric_description(description_id, metric_description: CompanyMetricDescriptionApiModelUpdateIn):
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            db_metric_desc = session.query(CompanyMetricDescription).filter(CompanyMetricDescription.id == description_id).first()
            if db_metric_desc is None:
                raise HTTPException(status_code=500, detail="No metric description with id: " + description_id + " exists.")
            
            if metric_description.code is not None:
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

@router.delete("/description/{description_id}")
def delete_company_metric_description(description_id):
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            session.query(CompanyMetricDescription).filter(CompanyMetricDescription.id == description_id).delete()
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))


@router.post("/description/note/{metric_description_id}", status_code=status.HTTP_201_CREATED, response_model=CompanyMetricDescriptionNoteApiModelOut)
def save_company_metric_description_note(metric_description_id, description_note: CompanyMetricDescriptionNoteApiModelIn):
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            existing_metric_desc = session.query(CompanyMetricDescription).filter(CompanyMetricDescription.id == metric_description_id).first()
            if existing_metric_desc is None:
                raise HTTPException(status_code=500, detail="No metric description with id: " + metric_description_id + " exists.")
            
            binary_data = description_note.data
            if description_note.note_type != NOTE_TYPE_TEXT:
                binary_data = base64.b64decode(description_note.data)
            
            if description_note.note_type == NOTE_TYPE_TEXT:
                binary_data = binary_data.encode('ascii')
            
            db_desc_note = CompanyMetricDescriptionNote(note_data=binary_data, note_type=description_note.note_type)
            session.add(db_desc_note)
            session.flush()

            if description_note.company_ids is None or len(description_note.company_ids) == 0:
                metric_relation = CompanyMetricRelation(company_id=None, company_metric_description_id=int(metric_description_id), company_metric_description_note_id=db_desc_note.id)
                session.add(metric_relation)
            else:                
                for company_id in description_note.company_ids:              
                    metric_relation = CompanyMetricRelation(company_id=company_id, company_metric_description_id=int(metric_description_id), company_metric_description_note_id=db_desc_note.id)
                    session.add(metric_relation)
            
            session.add(db_desc_note)

            session.flush()
            ret = CompanyMetricDescriptionNoteApiModelOut(note_id=db_desc_note.id, metric_description_id=metric_description_id, data=base64.b64encode(binary_data), note_type=db_desc_note.note_type, company_ids=description_note.company_ids)
            return ret

    except ValidationError as val_err:
        raise HTTPException(status_code=500, detail=str(val_err))
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))

#you can add, delete companies that share the note for same desc
#you can change data/note type
#done separetely
@router.post("/description/note/{metric_description_id}/{note_id}")
def update_company_metric_description_note(metric_description_id, note_id, description_note: CompanyMetricDescriptionNoteApiModelIn):
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            existing_metric_desc = session.query(CompanyMetricDescription).filter(CompanyMetricDescription.id == metric_description_id).first()
            if existing_metric_desc is None:
                raise HTTPException(status_code=500, detail="No metric description with id: " + metric_description_id + " exists.")

            existing_db_note = session.query(CompanyMetricDescriptionNote).filter(CompanyMetricDescriptionNote.id == note_id).first()
            if existing_db_note is None:
                raise HTTPException(status_code=500, detail="No metric description note with id: " + note_id + " exists.")
            
            binary_data = description_note.data
            if description_note.note_type != NOTE_TYPE_TEXT:
                binary_data = base64.b64decode(description_note.data)
            
            if description_note.note_type == NOTE_TYPE_TEXT:
                binary_data = binary_data.encode('ascii')
            
            existing_db_note.note_data = binary_data
            existing_db_note.note_type = description_note.note_type

            existing_metrics_relations = session.query(CompanyMetricRelation).filter(CompanyMetricRelation.company_metric_description_id == metric_description_id, \
                                                       CompanyMetricRelation.company_metric_description_note_id == note_id).all()

            if description_note.company_ids is None or len(description_note.company_ids) == 0:
                for mr in existing_metrics_relations:
                    session.delete(mr)
                metric_relation = CompanyMetricRelation(company_id=None, company_metric_description_id=int(metric_description_id), company_metric_description_note_id=existing_db_note.id)
                session.add(metric_relation)
                '''for relation in existing_metrics_relations:
                    if relation.company_id is not None:
                        session.delete(relation)'''
            else:
                for mr in existing_metrics_relations:
                    session.delete(mr)
                session.flush()
                for company_id in description_note.company_ids:              
                    metric_relation = CompanyMetricRelation(company_id=company_id, company_metric_description_id=int(metric_description_id), company_metric_description_note_id=existing_db_note.id)
                    session.add(metric_relation)
                '''it = next((x for x in description_note.company_ids if x == relation.company_id), None)
                if it == None:
                    session.delete(relation)'''
            
            session.flush()
            ret = CompanyMetricDescriptionNoteApiModelOut(note_id=existing_db_note.id, metric_description_id=metric_description_id, data=base64.b64encode(binary_data), note_type=existing_db_note.note_type, company_ids=description_note.company_ids)
            return ret
                    
    except ValidationError as val_err:
        raise HTTPException(status_code=500, detail=str(val_err))
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))

@router.delete("/description/note/{note_id}")
def delete_company_metric_description_note(note_id):
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            session.query(CompanyMetricDescriptionNote).filter(CompanyMetricDescriptionNote.id == note_id).delete()
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))


@router.post("/{company_id}/{description_id}", status_code=status.HTTP_201_CREATED)
def save_company_metric(company_id, description_id, metric: CompanyMetricApiModelIn):
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            db_metric = CompanyMetric(company_id=company_id, company_metric_description_id=description_id, data=metric.data, look_back=metric.look_back, date_recorded=metric.date_recorded)
            session.add(db_metric)

            session.flush()
            ret = CompanyMetricApiModelOut(id=db_metric.id, data=db_metric.data, look_back=db_metric.look_back, date_recorded=db_metric.date_recorded)
            return ret
    except ValidationError as val_err:
        raise HTTPException(status_code=500, detail=str(val_err))
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))

@router.post("/{company_id}/{description_id}/{metric_id}")
def update_company_metric(company_id, metric_id, metric: CompanyMetricApiModelIn):
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            db_metric = session.query(CompanyMetric).filter(CompanyMetric.id == metric_id).first()
            if db_metric is None:
                raise HTTPException(status_code=500, detail="No metric with id: " + metric_id + " exists.")

            db_metric.data = metric.data
            db_metric.look_back = metric.look_back
            db_metric.date_recorded = metric.date_recorded

            session.flush()
            ret = CompanyMetricApiModelOut(id=db_metric.id, data=db_metric.data, look_back=db_metric.look_back, date_recorded=db_metric.date_recorded)
            return ret
    except ValidationError as val_err:
        raise HTTPException(status_code=500, detail=str(val_err))
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))

@router.delete("/{metric_id}")
def delete_company_metric(metric_id):
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            session.query(CompanyMetric).filter(CompanyMetric.id == metric_id).delete()
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))