from fastapi.testclient import TestClient

from api.server import app

from api.config import init_config

import sys, os, json, pytest

from  test.test_utils import cleanup_db_from_db_str, create_default_groups, create_default_industries, create_default_industry_relations, create_default_metric_classifications, create_default_metric_descriptions, create_default_sector_relations, create_default_sectors, create_default_users, get_access_tokens

from py_common_utils_gh.db_utils.db_utils import SqlAlchemySessionManager

from db.models import *

from  test.test_utils import cleanup_db_from_db_str, create_default_business_segments, create_default_companies, create_system_user

import api.constants as api_constants
from passlib.context import CryptContext

client = TestClient(app)

class TestMetricDataApi:
    @classmethod
    def setup_class(cls):
        try:
            TestMetricDataApi.base_url = "/" + api_constants.app_name + "/" + api_constants.version

            absolute_path = os.path.join(sys.path[0], 'config.json')
            with open(absolute_path, 'r') as f:
                file_content_raw = f.read()
                config_json_content = json.loads(file_content_raw)
                init_config(config_json_content)
                TestMetricDataApi.db_conn_str = config_json_content['dbConnString']

            manager = SqlAlchemySessionManager()
            with manager.session_scope(db_url=TestMetricDataApi.db_conn_str, template_name='default_session') as session:
                cleanup_db_from_db_str(TestMetricDataApi.db_conn_str)
                           
                create_default_users(session)

                create_default_companies(session)

                create_default_business_segments(session)

                create_default_metric_classifications(session)

                create_default_metric_descriptions(session)

            
            toks = get_access_tokens(client, TestMetricDataApi.base_url, [('system', 'system'), ('ghelie', 'ghelie123')])
            TestMetricDataApi.system_access_token = toks[0]
            TestMetricDataApi.ghelie_access_token = toks[1]

        
        except Exception as gen_ex:
            print(str(gen_ex))

    def test_create_metric_data(self):
        base_url = TestMetricDataApi.base_url + "/metric/data"
        
        body = {'metric_description_id': 1, 'business_segment_id': 1, 'data': 6500}
        response = client.post(base_url, headers={"Authorization": "Bearer " + TestMetricDataApi.ghelie_access_token}, json=body)             
        assert response.status_code == 201
        response = response.json()
        assert response['id'] is not None

        body = {'metric_description_id': 1, 'business_segment_id': 1, 'data': 5000}
        response = client.post(base_url, headers={"Authorization": "Bearer " + TestMetricDataApi.system_access_token}, json=body)             
        assert response.status_code == 201
        response = response.json()
        assert response['id'] is not None

        body = {'metric_description_id': 1, 'business_segment_id': 2, 'data': 3000}
        response = client.post(base_url, headers={"Authorization": "Bearer " + TestMetricDataApi.system_access_token}, json=body)             
        assert response.status_code == 201
        response = response.json()
        assert response['id'] is not None


        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=TestMetricDataApi.db_conn_str, template_name='default_session') as session:
            db_metric_data = session.query(MetricData).all()
            assert len(db_metric_data) == 3
            db_metric_data.sort(key=lambda x: x.id, reverse=False)
            assert db_metric_data[0].metric_description_id == 1
            assert db_metric_data[0].company_business_segment_id == 1
            assert db_metric_data[0].data == 6500
            assert db_metric_data[0].user_id == 2

            assert db_metric_data[1].metric_description_id == 1
            assert db_metric_data[1].company_business_segment_id == 1
            assert db_metric_data[1].data == 5000
            assert db_metric_data[1].user_id == 1

            assert db_metric_data[2].metric_description_id == 1
            assert db_metric_data[2].company_business_segment_id == 2
            assert db_metric_data[2].data == 3000
            assert db_metric_data[2].user_id == 1


    def test_update_metric_data(self):
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=TestMetricDataApi.db_conn_str, template_name='default_session') as session:
            session.query(MetricData).delete()
            session.add(MetricData(id=1000, metric_description_id=3, company_business_segment_id=3, user_id=1, data=8000))

        base_url = TestMetricDataApi.base_url + "/metric/data"
        url = base_url + "/" + str(1000)
        body = {'metric_description_id': 7, 'business_segment_id': 677, 'data': 450}
        response = client.put(url, headers={"Authorization": "Bearer " + TestMetricDataApi.ghelie_access_token}, json=body)             
        assert response.status_code == 204

        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=TestMetricDataApi.db_conn_str, template_name='default_session') as session:
            db_metric_data = session.query(MetricData).filter(MetricData.id == 1000).all()
            assert len(db_metric_data) == 1
            assert db_metric_data[0].metric_description_id == 3
            assert db_metric_data[0].company_business_segment_id == 3
            assert db_metric_data[0].data == 450
            assert db_metric_data[0].user_id == 1

    def test_delete_metric_data(self):
        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=TestMetricDataApi.db_conn_str, template_name='default_session') as session:
            session.query(MetricData).delete()
            session.add(MetricData(id=1000, metric_description_id=3, company_business_segment_id=3, user_id=1, data=8000))

        base_url = TestMetricDataApi.base_url + "/metric/data"
        url = base_url + "/" + str(1000)
        response = client.delete(url, headers={"Authorization": "Bearer " + TestMetricDataApi.system_access_token})             
        assert response.status_code == 204

        manager = SqlAlchemySessionManager()
        with manager.session_scope(db_url=TestMetricDataApi.db_conn_str, template_name='default_session') as session:
            db_metric_data = session.query(MetricData).filter(MetricData.id == 1000).all()
            assert len(db_metric_data) == 0