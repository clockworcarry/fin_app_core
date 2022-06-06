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

import datetime, base64

import simplejson as json

import api.config as api_config

router = APIRouter(
    prefix="/company/metric",
    tags=["companyMetric"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)

class CompanyMetricDescriptionNoteApiModelOut(BaseModel):
    data: bytes = None
    note_type: int = None

class CompanyMetricDescriptionApiModelIn(BaseModel):
    code: str
    display_name: str
    metric_data_type: int
    metric_duration: int = None
    metric_duration_type: int
    look_back: bool = False
    year_recorded: int
    quarter_recorded: int = None
    metric_fixed_year: int = None
    metric_fixed_quarter: int = None

    group_ids: List[int] = None
    
    #notes: List[CompanyMetricDescriptionNoteApiModelIn]

class CompanyMetricDescriptionApiModelOut(BaseModel):
    id: int
    code: str
    display_name: str
    metric_data_type: int
    metric_duration: int
    metric_duration_type: int
    look_back: bool
    year_recorded: int = None
    quarter_recorded: int = None
    metric_fixed_year: int = None
    metric_fixed_quarter: int = None

    metric_relation_ids: List[int]
    group_ids: List[int]

    
    #notes: List[CompanyMetricDescriptionNoteApiModelOut] too big

class CompanyMetricApiModelOut(BaseModel):
    data: float
    description: CompanyMetricDescriptionApiModelOut

class CompanyMetricApiModelIn(BaseModel):
    data: float
    company_segment_id: int
    company_metric_relation_id: int

class CompanyMetricDescriptionNoteApiModelIn(BaseModel):
    data: str
    note_type: int
    company_ids: List[int] = None #list of companies this note applies to. if None, applies to all companies

class CompanyMetricDescriptionNoteApiModelOut(BaseModel):
    metric_description_id: int
    note_id: int
    data: str
    note_type: int

'''class CompanyMetricDescriptionNoteApiModelOut(BaseModel):
    data: str
    note_type: int
    company_ids: List[int] = None #list of companies this note applies to. if None, applies to all companies'''



@router.post("/description/note", status_code=status.HTTP_201_CREATED, response_model=CompanyMetricDescriptionNoteApiModelOut)
def save_company_metric_description_note(description_note: CompanyMetricDescriptionNoteApiModelIn):
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            binary_data = description_note.data
            if description_note.note_type != NOTE_TYPE_TEXT:
                binary_data = base64.b64decode(description_note.data)
            
            if description_note.note_type == NOTE_TYPE_TEXT:
                binary_data = binary_data.encode('ascii')
            
            db_desc_note = CompanyMetricDescriptionNote(note_data=binary_data, note_type=description_note.note_type)
            session.add(db_desc_note)
            session.flush()

            '''if description_note.company_ids is None or len(description_note.company_ids) == 0:
                metric_relation = CompanyMetricRelation(company_id=None, company_metric_description_id=int(metric_description_id), company_metric_description_note_id=db_desc_note.id)
                session.add(metric_relation)
            else:                
                for company_id in description_note.company_ids:              
                    metric_relation = CompanyMetricRelation(company_id=company_id, company_metric_description_id=int(metric_description_id), company_metric_description_note_id=db_desc_note.id)
                    session.add(metric_relation)
            
            session.add(db_desc_note)'''

            session.flush()
            ret_data = None
            if db_desc_note.note_type == NOTE_TYPE_TEXT_DOC:
                ret_data = base64.b64encode(db_desc_note.note_data)

            return CompanyMetricDescriptionNoteApiModelOut(note_id=db_desc_note.id, metric_description_id=metric_description_id, data=ret_data, note_type=db_desc_note.note_type)

    except ValidationError as val_err:
        raise HTTPException(status_code=500, detail=str(val_err))
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))

@router.get("/{bop_id}")
def get_company_metrics(bop_id, loadDescriptions: Optional[bool] = True, loadDescriptionsNotes: Optional[bool] = False, response_model=List[CompanyMetricApiModelOut]):
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
                    out_desc = CompanyMetricDescriptionApiModelOut(id=md[1].id, code=md[1].code, display_name=md[1].display_name, metric_data_type=md[1].metric_data_type,
                                                                    metric_duration=md[1].metric_duration, metric_duration_type=md[1].metric_duration_type, look_back=md[1].look_back,
                                                                    year_recorded=md[1].year_recorded, quarter_recorded=md[1].quarter_recorded, metric_fixed_year=md[1].metric_fixed_year,
                                                                    metric_fixed_quarter=md[1].metric_fixed_quarter, group_ids=md[1].group_ids)
                    
                    new_metric = CompanyMetricApiModelOut(data=md[0].data, description=out_desc)
                    resp.append(new_metric)
            
            return resp

    except ValidationError as val_err:
        raise HTTPException(status_code=500, detail=str(gen_ex))
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))

@router.get("/descriptions/{group_id}", status_code=status.HTTP_200_OK, response_model=List[CompanyMetricDescriptionApiModelOut])
def get_company_metric_descriptions(group_id, loadDescriptionsNotes: Optional[bool] = True):
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            query_res = session.query(CompanyMetricDescription) \
                               .join(CompanyMetricRelation, CompanyMetricRelation.company_metric_description_id == CompanyMetricDescription.id) \
                               .filter(or_(CompanyMetricRelation.company_group_id == group_id, CompanyMetricRelation.company_group_id == None)).all()

            resp = []
            
            for res in query_res:
                db_relations = session.query(CompanyMetricRelation).filter(CompanyMetricRelation.company_metric_description_id == res.id).all()
                group_ids = []
                metric_relation_ids = []
                for dr in db_relations:
                    gid = dr.company_group_id
                    if gid is None:
                        gid = 0
                    group_ids.append(gid)
                    metric_relation_ids.append(dr.id)

                    #display notes instead of relation ids

                resp.append(CompanyMetricDescriptionApiModelOut(id=res.id, code=res.code, display_name=res.display_name, metric_data_type=res.metric_data_type,
                                                                metric_duration=res.metric_duration, metric_duration_type=res.metric_duration_type, look_back=res.look_back,
                                                                year_recorded=res.year_recorded, quarter_recorded=res.quarter_recorded, metric_fixed_year=res.metric_fixed_year,
                                                                metric_fixed_quarter=res.metric_fixed_quarter, group_ids=group_ids))
            
            return resp

    except ValidationError as val_err:
        raise HTTPException(status_code=500, detail=str(val_err))
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))

@router.post("/description", status_code=status.HTTP_201_CREATED, response_model=CompanyMetricDescriptionApiModelOut)
def create_company_metric_description(body: CompanyMetricDescriptionApiModelIn):
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            new_desc = CompanyMetricDescription(code=body.code, display_name=body.display_name, metric_data_type=body.metric_data_type, metric_duration=body.metric_duration, 
                                                metric_duration_type=body.metric_duration_type, look_back=body.look_back)
            session.add(new_desc)                     
            session.flush()

            if body.group_ids is not None:
                for gid in body.group_ids:
                    session.add(CompanyMetricRelation(company_metric_description_id=new_desc.id, company_group_id=gid))
            
            return CompanyMetricDescriptionApiModelOut(id=new_desc.id, code=new_desc.code, display_name=new_desc.display_name, metric_data_type=new_desc.metric_data_type,
                                                       metric_duration=new_desc.metric_duration, metric_duration_type=new_desc.metric_duration_type, look_back=new_desc.look_back,
                                                       year_recorded=new_desc.year_recorded, quarter_recorded=new_desc.quarter_recorded, metric_fixed_year=new_desc.metric_fixed_year,
                                                       metric_fixed_quarter=new_desc.metric_fixed_quarter)
    
    except ValidationError as val_err:
        raise HTTPException(status_code=500, detail=str(val_err))
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))

@router.put("/description/{description_id}")
def update_company_metric_description(description_id, body: CompanyMetricDescriptionApiModelIn):
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            db_metric_desc = session.query(CompanyMetricDescription).filter(CompanyMetricDescription.id == description_id).first()
            if db_metric_desc is None:
                raise HTTPException(status_code=500, detail="No metric description with id: " + str(description_id) + " exists.")
            
            db_metric_desc.code = body.code
            db_metric_desc.display_name = body.display_name
            db_metric_desc.metric_data_type = body.metric_data_type
            db_metric_desc.metric_duration = body.metric_duration
            db_metric_desc.metric_duration_type = body.metric_data_type
            db_metric_desc.look_back = body.look_back
            db_metric_desc.year_recorded = body.year_recorded
            db_metric_desc.quarter_recorded = body.quarter_recorded
            db_metric_desc.metric_fixed_year = body.metric_fixed_year
            db_metric_desc.metric_fixed_quarter = body.metric_fixed_quarter

            db_relation = session.query(CompanyMetricRelation).filter(CompanyMetricRelation.company_metric_description_id == description_id).delete()

            if body.group_ids is not None:
                for gid in body.group_ids:
                    session.add(CompanyMetricRelation(company_metric_description_id=description_id, company_group_id=gid))
            else:
                session.add(CompanyMetricRelation(company_metric_description_id=description_id, company_group_id=None))

            if body.group_ids is None:
                body.group_ids = []


            return CompanyMetricDescriptionApiModelOut(id=db_metric_desc.id, code=db_metric_desc.code, display_name=db_metric_desc.display_name, metric_data_type=db_metric_desc.metric_data_type,
                                                       metric_duration=db_metric_desc.metric_duration, metric_duration_type=db_metric_desc.metric_duration_type, look_back=db_metric_desc.look_back,
                                                       year_recorded=db_metric_desc.year_recorded, quarter_recorded=db_metric_desc.quarter_recorded, metric_fixed_year=db_metric_desc.metric_fixed_year,
                                                       metric_fixed_quarter=db_metric_desc.metric_fixed_quarter, group_ids=body.group_ids)

    except ValidationError as val_err:
        raise HTTPException(status_code=500, detail=str(val_err))
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))

@router.put("/description/{description_id}")
def update_company_metric_description_groups(description_id, body: CompanyMetricDescriptionApiModelIn):
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            db_metric_desc = CompanyMetricDescription()
            db_metric_desc.id = description_id
            db_metric_desc.code = body.code
            db_metric_desc.display_name = body.display_name
            db_metric_desc.metric_data_type = body.metric_data_type
            db_metric_desc.metric_duration = body.metric_duration
            db_metric_desc.metric_duration_type = body.metric_data_type
            db_metric_desc.look_back = body.look_back
            db_metric_desc.year_recorded = body.year_recorded
            db_metric_desc.quarter_recorded = body.quarter_recorded
            db_metric_desc.metric_fixed_year = body.metric_fixed_year
            db_metric_desc.metric_fixed_quarter = body.metric_fixed_quarter

            session.add(db_metric_desc)

            db_relation = session.query(CompanyMetricRelation).filter(CompanyMetricRelation.company_metric_description_id == description_id).all()

            return CompanyMetricDescriptionApiModelOut(id=db_metric_desc.id, code=db_metric_desc.code, display_name=db_metric_desc.display_name, metric_data_type=db_metric_desc.metric_data_type,
                                                       metric_duration=db_metric_desc.metric_duration, metric_duration_type=db_metric_desc.metric_duration_type, look_back=db_metric_desc.look_back,
                                                       year_recorded=db_metric_desc.year_recorded, quarter_recorded=db_metric_desc.quarter_recorded, metric_fixed_year=db_metric_desc.metric_fixed_year,
                                                       metric_fixed_quarter=db_metric_desc.metric_fixed_quarter)

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


@router.post("/{company_id}/{bop_id}/{description_id}", status_code=status.HTTP_201_CREATED)
def save_company_metric(company_id, bop_id, description_id, body: CompanyMetricApiModelIn):
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            new_metric = CompanyMetric(date_recorded=body.date_recorded, data=body.data, look_back=body.look_back, company_metric_description_id=description_id, company_business_or_product_id=bop_id)          
            session.add(new_metric)
            session.flush()
            return CompanyMetricApiModelOut(id=new_metric.id, data=new_metric.data, look_back=new_metric.look_back, date_recorded=new_metric.date_recorded)
    
    except ValidationError as val_err:
        raise HTTPException(status_code=500, detail=str(val_err))
    except Exception as gen_ex:
        raise HTTPException(status_code=500, detail=str(gen_ex))

@router.put("/{metric_id}", status_code=status.HTTP_200_OK)
def update_company_metric(company_id, metric_id, body: CompanyMetricApiModelIn):
    try:
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=api_config.global_api_config.db_conn_str, template_name='default_session') as session:
            db_metric = session.query(CompanyMetric).filter(CompanyMetric.id == metric_id).first()
            if db_metric is None:
                raise HTTPException(status_code=500, detail="No metric with id: " + metric_id + " exists.")

            db_metric.data = body.data
            db_metric.look_back = body.look_back
            db_metric.date_recorded = body.date_recorded

            return CompanyMetricApiModelOut(id=db_metric.id, data=db_metric.data, look_back=db_metric.look_back, date_recorded=db_metric.date_recorded)
            
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