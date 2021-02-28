import falcon

from py_common_utils_gh.os_common_utils import setup_logger, default_log_formatter
from py_common_utils_gh.db_utils.db_utils import SqlAlchemySessionManager
from db.models import *
import numpy as np
from psycopg2 import *
from sqlalchemy import create_engine, select, insert, exists
from sqlalchemy.orm import sessionmaker

import simplejson as json

import config

class CompanyMetricsResource(object):
    def on_get(self, req, resp, company_id):
        try:
            manager = SqlAlchemySessionManager()
            with manager.session_scope(db_url=config.global_api_config.db_conn_str, template_name='default_session') as session:
                load_descriptions = True
                if 'loadDescriptions' in req.params and not req.params['loadDescriptions']:
                    load_descriptions = False
                
                load_descriptions_note = True
                if 'loadDescriptionsNotes' in req.params and not req.params['loadDescriptionsNotes']:
                    load_descriptions_note = False

                query_res = session.query(CompanyMetric, CompanyMetricDescription, CompanyMetricDescriptionNote) \
                                                      .join(CompanyMetricDescription, CompanyMetric.company_metric_description_id == CompanyMetricDescription.id) \
                                                      .outerjoin(CompanyMetricDescriptionNote, CompanyMetricDescriptionNote.company_metric_description_id == CompanyMetricDescription.id) \
                                                      .filter(CompanyMetric.company_id == company_id).order_by(CompanyMetric.date_recorded.desc()).all()
                
                
                #metrics = query_res[0]
                #for res in query_res:

                
                resp.body = {}
                resp.body['metrics'] = []
                for res in query_res:
                    new_metric = {}
                    new_metric['code'] = res[1].code
                    new_metric['displayName'] = res[1].display_name
                    new_metric['metricDataType'] = res[1].metric_data_type
                    new_metric['notes'] = []
                    for note in res[1].notes:
                        json_note = {}
                        json_note['data'] = note.note_data.decode('ascii')
                        json_note['type'] = note.note_type
                        new_metric['notes'].append(json_note)
                    
                    new_metric['data'] = res[0].data
                    new_metric['dateRecorded'] = res[0].date_recorded
                    new_metric['lookBack'] = res[0].look_back
                    
                    resp.body['metrics'].append(new_metric)
                
                resp.body = json.dumps(resp.body, default=str)
                
        except Exception as gen_ex:
            print(str(gen_ex))

class CompanyMetricsDescriptionResource(object):
    def on_get(self, req, resp):
        try:
            manager = SqlAlchemySessionManager()
            with manager.session_scope(db_url=config.global_api_config.db_conn_str, template_name='default_session') as session:
                metrics = session.query(CompanyMetricDescription).all()

                resp.body = {}
                resp.body['metrics'] = []
                for metric in metrics:
                    resp.body['metrics'].append({"data": metric.data})
                
                resp.body = json.dumps(resp.body)
                
        except Exception as gen_ex:
            print(str(gen_ex))
